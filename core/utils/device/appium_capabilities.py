class AppiumCapabilities(object):
    def __init__(self, platform_name=None, platform_version=None, automation_name=None, device_name=None,
                 bundle_id=None, app_package=None, app_activity=None):
        self.platformName = platform_name
        self.platformVersion = platform_version
        self.automationName = automation_name
        self.deviceName = device_name
        self.bundleId = bundle_id
        self.appPackage = app_package
        self.appActivity = app_activity
        self.noReset = True
