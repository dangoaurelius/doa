from config import Config
from doaProvider import DoaProvider
from doaPresenterConsole import DoaPresenter as DoaConsolePresenter
from doaPresenterUi import DoaPresenter as DoaUiPresenter
from doaPresenterCompass import DoaPresenter as DoaCompassPresenter

calibration = 0
defaultPlutoIp = '192.168.2.1'

f410 = Config(defaultPlutoIp, 4.1e8, 10e3, calibration)
f2300 = Config(defaultPlutoIp, 2.3e9, 200e3, calibration)

doaProvider = DoaProvider(f410)

consoleDoaPresenter = DoaConsolePresenter(doaProvider)

consoleDoaPresenter.run(-10)