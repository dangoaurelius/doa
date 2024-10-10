import adi
import numpy as np

class DoaProvider:
  def __init__(self, config):
    self.config = config

    try:
      self.sdr = self.connect()

      if self.sdr:
       self.setup()
    except:
      print("Cant connect to pluto plus")

  def connect(self):
    return adi.ad9361(uri='ip:{}'.format(self.config.ip))

  def calculateAntennaDistance(self):
    wavelength = 3e8 / self.config.frequency
    return 0.5 * wavelength 

  def setup(self):
    self.sdr.rx_enabled_channels    = [0, 1]
    self.sdr.sample_rate            = int(self.config.samp_rate)
    self.sdr.rx_rf_bandwidth        = int(self.config.fc0 * 3)
    self.sdr.rx_lo                  = int(self.config.frequency)
    self.sdr.rx_hardwaregain_chan0  = int(self.config.rx_gain0)
    self.sdr.rx_hardwaregain_chan1  = int(self.config.rx_gain1)
    self.sdr.rx_buffer_size         = int(self.config.numSamples)
    self.sdr.gain_control_mode      = self.config.rx_mode
    self.sdr._rxadc.set_kernel_buffers_count(1)

    # configuretion for calibration transmition
    self.sdr.tx_rf_bandwidth       = int(self.config.fc0 * 3)
    self.sdr.tx_lo                 = int(self.config.frequency)
    self.sdr.tx_cyclic_buffer      = True
    self.sdr.tx_hardwaregain_chan0 = int(self.config.tx_gain)
    self.sdr.tx_hardwaregain_chan1 = int(-88)
    self.sdr.tx_buffer_size        = int(2**18)

    fs = int(self.sdr.sample_rate)
    ts = 1 / float(fs)

    xf = np.fft.fftfreq(self.config.numSamples, ts)
    xf = np.fft.fftshift(xf) / 1e6

    self.signal_start = int(self.config.numSamples * (self.config.samp_rate / 2 + self.config.fc0 / 2) / self.config.samp_rate)
    self.signal_end = int(self.config.numSamples * (self.config.samp_rate / 2 + self.config.fc0 * 2) / self.config.samp_rate)
    
    self.antenna_distance = self.calculateAntennaDistance()

  def calcTheta(self, phase):
    # calculates the steering angle for a given phase delta (phase is in deg)
    # steering angle is theta = arcsin(c*deltaphase/(2*pi*f*d)
    arcsin_arg = np.deg2rad(phase) * 3E8 / (2 * np.pi * self.config.frequency * self.antenna_distance)
    arcsin_arg = max(min(1, arcsin_arg), -1) # arcsin argument must be between 1 and -1, or numpy will throw a warning
    
    calc_theta = np.rad2deg(np.arcsin(arcsin_arg))
    
    return calc_theta

  def dbfs(self, raw_data):
    # function to convert IQ samples to FFT plot, scaled in dBFS
    NumSamples = len(raw_data)
    win = np.hamming(NumSamples)
    y = raw_data * win
    s_fft = np.fft.fft(y) / np.sum(win)
    s_shift = np.fft.fftshift(s_fft)
    s_dbfs = 20 * np.log10(np.abs(s_shift) / (2**11))     # Pluto is a signed 12 bit ADC, so use 2^11 to convert to dBFS

    return s_shift, s_dbfs

  def monopulse_angle(self, array1, array2):
    # Since our signals are closely aligned in time, we can just return the 'valid' case where the signals completley overlap
    # We can do correlation in the time domain (probably faster) or the freq domain
    # In the time domain, it would just be this:
    # sum_delta_correlation = np.correlate(delayed_sum, delayed_delta, 'valid')
    # But I like the freq domain, because then I can focus just on the fc0 signal of interest
    sum_delta_correlation = np.correlate(array1[self.signal_start:self.signal_end], array2[self.signal_start:self.signal_end], 'valid')
    angle_diff = np.angle(sum_delta_correlation)

    return angle_diff

  def scan_for_DOA(self):
    # go through all the possible phase shifts and find the peak, that will be the DOA (direction of arrival) aka steer_angle
    data = self.sdr.rx()
    Rx_0 = data[0]
    Rx_1 = data[1]
    peak_sum = []
    peak_delta = []
    monopulse_phase = []

    delay_phases = np.arange(-180, 180, 2) # phase delay in degrees
    for phase_delay in delay_phases:   
        delayed_Rx_1 = Rx_1 * np.exp(1j * np.deg2rad(phase_delay + self.config.phaseCal))

        delayed_sum = Rx_0 + delayed_Rx_1
        delayed_delta = Rx_0 - delayed_Rx_1

        delayed_sum_fft, delayed_sum_dbfs = self.dbfs(delayed_sum)
        delayed_delta_fft, delayed_delta_dbfs = self.dbfs(delayed_delta)

        mono_angle = self.monopulse_angle(delayed_sum_fft, delayed_delta_fft)
        
        peak_sum.append(np.max(delayed_sum_dbfs))
        peak_delta.append(np.max(delayed_delta_dbfs))
        monopulse_phase.append(np.sign(mono_angle))
        
    peak_dbfs = np.max(peak_sum)
    peak_delay_index = np.where(peak_sum==peak_dbfs)
    peak_delay = delay_phases[peak_delay_index[0][0]]
    steer_angle = int(self.calcTheta(peak_delay))
    
    return delay_phases, peak_dbfs, peak_delay, steer_angle, peak_sum, peak_delta, monopulse_phase  

  def start_calibration_transmit(self):
    fs = int(self.sdr.sample_rate)

    N = 2**16
    ts = 1 / float(fs)
    t = np.arange(0, N * ts, ts)
    i0 = np.cos(2 * np.pi * t * self.config.fc0) * 2 ** 14
    q0 = np.sin(2 * np.pi * t * self.config.fc0) * 2 ** 14
    iq0 = i0 + 1j * q0

    self.sdr.tx([iq0, iq0])  # Send Tx data.
  
  def stop_calibration_transmit(self):
    self.sdr.tx_destroy_buffer()

