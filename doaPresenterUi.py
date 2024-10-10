import matplotlib.pyplot as plt

class DoaPresenter:
  def __init__(self, doaProvider) -> None:
    self.provider = doaProvider
    plt.ion()

  def getDoa(self):
    delay_phases, peak_dbfs, peak_delay, steer_angle, peak_sum, peak_delta, monopulse_phase = self.provider.scan_for_DOA()

    return steer_angle

  def run(self, threshhold):
    try:
      while True: 
        delay_phases, peak_dbfs, peak_delay, steer_angle, peak_sum, peak_delta, monopulse_phase = self.provider.scan_for_DOA()

        plt.plot(delay_phases, peak_sum)
        plt.plot(delay_phases, peak_delta)
        plt.plot(delay_phases, monopulse_phase)

        plt.axvline(x=peak_delay, color='r', linestyle=':')

        plt.text(-180, -26, "Peak signal occurs with phase shift = {} deg".format(round(peak_delay,1)))
        plt.text(-180, -28, "If d={}mm, then steering angle = {} deg".format(int(self.provider.antenna_distance * 1000), steer_angle))
        
        plt.ylim(top = 5, bottom = -30)        
        
        plt.xlabel("phase shift [deg]")
        plt.ylabel("Rx0 + Rx1 [dBfs]")
        
        plt.draw()
        plt.pause(0.25)
        plt.clf()

    except KeyboardInterrupt:
      print("Exiting...")
