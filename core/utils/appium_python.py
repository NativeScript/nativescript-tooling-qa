from appium import webdriver
from appium.webdriver.appium_service import AppiumService


class AppiumDriver(object):
    def __init__(self, capabilities):
        self.appium_service = AppiumService()
        self.appium_service.start()
        self.capabilities = capabilities
        self.executor = 'http://0.0.0.0:4723/wd/hub'
        self.driver = webdriver.Remote(self.executor, capabilities)

    def quit(self):
        self.appium_service.stop()
