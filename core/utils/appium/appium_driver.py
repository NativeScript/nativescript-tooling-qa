from appium import webdriver
from appium.webdriver.appium_service import AppiumService, DEFAULT_PORT

from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.process import Process


# noinspection PyDictCreation
class AppiumDriver(object):
    service = None
    driver = None

    def __init__(self, platform, device, bundle_id, activity='com.tns.NativeScriptActivity', wait_timeout=30):
        """
        Init appium session.
        :param platform: Platform enum value.
        :param device: device instance.
        :param bundle_id: bundle id of application under test (must be already deployed on device).
        :param activity: default app activity (needed in Android only).
        :param wait_timeout: timeout for finding elements (in seconds).
        """
        capabilities = self.__get_capabilities(platform=platform, device=device, bundle_id=bundle_id, activity=activity)
        self.__start_server()
        self.__start_client(capabilities, wait_timeout)

    def stop(self):
        """
        Stop appium session.
        """
        self.__stop_client()
        self.__stop_server()

    @staticmethod
    def kill():
        """
        Kill all instance of appium server.
        """
        Process.kill(proc_name='node', proc_cmdline='appium')

    def __start_server(self):
        Log.info("Starting appium server...")
        self.service = AppiumService()
        self.service.start(args=['-p', str(DEFAULT_PORT)])
        assert self.service.is_running, "Failed to start appium server."
        Log.info("Appium server started.")

    def __stop_server(self):
        if self.service is not None and self.service.is_running:
            self.service.stop()
            Log.info("Stop appium server.")

    @staticmethod
    def __get_capabilities(platform, device, bundle_id, activity='com.tns.NativeScriptActivity'):
        capabilities = {}
        capabilities['platformName'] = str(platform)
        capabilities['platformVersion'] = device.version
        capabilities['deviceName'] = device.name
        capabilities['udid'] = device.id
        capabilities['noReset'] = 'true'
        capabilities['fullReset'] = 'false'
        if platform == Platform.ANDROID:
            capabilities['automationName'] = 'uiautomator2'
            capabilities['appPackage'] = bundle_id
            capabilities['appActivity'] = activity
        if platform == Platform.IOS:
            capabilities['automationName'] = 'XCUITest'
            capabilities['bundleId'] = bundle_id
        # In case debug session is found increase 'newCommandTimeout' to allow debugging longer period of time.
        capabilities['newCommandTimeout'] = 3600 if Settings.IS_DEBUG else 60
        return capabilities

    def __start_client(self, capabilities, wait_timeout):
        Log.info("Starting appium client...")
        self.driver = webdriver.Remote('http://0.0.0.0:4723/wd/hub', capabilities)
        self.driver.implicitly_wait(wait_timeout)
        Log.info("Appium client started.")

    def __stop_client(self):
        if self.driver is not None:
            self.driver.quit()
            Log.info("Stop appium client.")
