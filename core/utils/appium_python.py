import psutil
from appium import webdriver

from core.settings import Settings


class AppiumDriver(object):
    def __init__(self, capabilities):
        psutil.Popen("appium --port 4723", cwd=Settings.TEST_RUN_HOME, shell=True, stdin=None, stdout=None,
                     stderr=None, close_fds=True)
        self.capabilities = capabilities
        self.executor = 'http://127.0.0.1:4723/wd/hub'
        self.driver = webdriver.Remote(self.executor, capabilities)
