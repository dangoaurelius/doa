from enum import Enum

class Config:
  def __init__(self, ip, frequency, dataFreq, phaseCalibraion) -> None:
    self.frequency = frequency
    self.ip = ip
    self.samp_rate = 2e6    # must be <=30.72 MHz if both channels are enabled
    self.numSamples = 2**12
    self.rx_mode = "manual"  # can be "manual" or "slow_attack"
    self.rx_gain0 = 40
    self.rx_gain1 = 40
    self.fc0 = int(dataFreq)
    self.phaseCal = phaseCalibraion
    
    self.tx_gain = -3
    