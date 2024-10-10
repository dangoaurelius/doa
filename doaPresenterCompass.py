import matplotlib.pyplot as plt
import numpy as np
import time

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
        if peak_dbfs >= threshhold:
          # fig = plt.figure(figsize=(3,3))
          ax = plt.subplot(111,polar=True)
          ax.set_theta_zero_location('N')
          ax.set_theta_direction(-1)
          ax.set_thetamin(-90)
          ax.set_thetamax(90)
          ax.set_rlim(bottom=-20, top=0)
          ax.set_yticklabels([])
          ax.vlines(np.deg2rad(steer_angle),0,-20)
          ax.text(-2, -14, "{} deg".format(steer_angle))

          plt.draw()
          plt.pause(0.25)
          plt.clf()
        else:
          time.sleep(0.25)

    except KeyboardInterrupt:
      print("Exiting...")
