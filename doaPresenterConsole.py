import time

class DoaPresenter:
  def __init__(self, doaProvider) -> None:
    self.provider = doaProvider


  def run(self, threshhold):
    try:
      while True: 
        delay_phases, peak_dbfs, peak_delay, steer_angle, peak_sum, peak_delta, monopulse_phase = self.provider.scan_for_DOA()
        if peak_dbfs >= threshhold:
          print("peek: {} peak delay: {} doa: {} deg".format(peak_dbfs, peak_delay, steer_angle))

        time.sleep(0.25)
    except KeyboardInterrupt:
      print("Exiting...")
