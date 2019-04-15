import unittest
import os
from appium import webdriver
from selenium.common.exceptions import InvalidSessionIdException
import pytest
import datetime


def pytest_configure(config):
    if not hasattr(config, 'slaveinput'):
        current_day = '{:%Y_%m_%d_%H_%S}'.format(datetime.datetime.now())
        ensure_dir('results')
        ensure_dir(os.path.join('slaveinput', current_day))
        result_dir = os.path.join(os.path.dirname(__file__), 'results', current_day)
        ensure_dir(result_dir)
        result_dir_test_run = result_dir
        ensure_dir(os.path.join(result_dir_test_run, 'screenshots'))
        ensure_dir(os.path.join(result_dir_test_run, 'logcat'))
        config.screen_shot_dir = os.path.join(result_dir_test_run, 'screenshots')
        config.logcat_dir = os.path.join(result_dir_test_run, 'logcat')


class DeviceLogger:
    def __init__(self, logcat_dir, screenshot_dir):
        self.screenshot_dir = screenshot_dir
        self.logcat_dir = logcat_dir


@pytest.fixture(scope='function')
def device_logger(request):
    logcat_dir = request.config.logcat_dir
    screenshot_dir = request.config.screen_shot_dir
    return DeviceLogger(logcat_dir, screenshot_dir)


if os.getenv('SAUCE_USERNAME') and os.getenv('SAUCE_ACCESS_KEY'):
    EXECUTOR = 'http://{}:{}@ondemand.saucelabs.com:80/wd/hub'.format(
        os.getenv('SAUCE_USERNAME'), os.getenv('SAUCE_ACCESS_KEY'))
else:
    EXECUTOR = 'http://127.0.0.1:4723/wd/hub'


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def take_screenhot_and_logcat(driver, device_logger, calling_request):
    __save_log_type(driver, device_logger, calling_request, 'logcat')


def take_screenhot_and_syslog(driver, device_logger, calling_request):
    __save_log_type(driver, device_logger, calling_request, 'syslog')


def __save_log_type(driver, device_logger, calling_request, type):
    logcat_dir = device_logger.logcat_dir
    screenshot_dir = device_logger.screenshot_dir

    try:
        driver.save_screenshot(os.path.join(screenshot_dir, calling_request + '.png'))
        logcat_data = driver.get_log(type)
    except InvalidSessionIdException:
        logcat_data = ''

    with open(os.path.join(logcat_dir, '{}_{}.log'.format(calling_request, type)), 'wb') as logcat_file:
        for data in logcat_data:
            data_string = '{}:  {}'.format(data['timestamp'], data['message'])
            logcat_file.write((data_string + '\n').encode('UTF-8'))

# ANDROID_APP_PATH = 'http://appium.github.io/appium/assets/ApiDemos-debug.apk' if os.getenv(
#     'SAUCE_LABS') else os.path.abspath('../apps/ApiDemos-debug.apk')
ANDROID_APP_PATH = \
    '/Users/dtodorov/SSD/nativescript-tooling-qa/TestApp/platforms/android/app/build/outputs/apk/debug/app-debug.apk'
# IOS_APP_PATH = 'http://appium.github.io/appium/assets/TestApp7.1.app.zip' if os.getenv(
    # 'SAUCE_LABS') else os.path.abspath('../apps/TestApp.app.zip')
IOS_APP_PATH = \
    '/Users/dtodorov/SSD/nativescript-tooling-qa/TestApp.zip'



iOS_capabilities={
    'platformName': 'iOS',
    'platformVersion': '12.0',
    'automationName': 'XCUITest',
    'deviceName': 'iPhoneXR_12',
    'app': IOS_APP_PATH
}

android_capabilities={
    'platformName': 'Android',
    'automationName': 'UIAutomator2',
    'platformVersion': '8.1',
    'deviceName': 'Emulator-Api27-Google',
    'app': ANDROID_APP_PATH,
}


class AppiumDriver:
    def __init__(self, capabilities, executor):
        self.capabilities = capabilities
        self.executor = executor

    def setUp(self):
        os.system('appium &')
        driver = webdriver.Remote(
            command_executor=EXECUTOR,
            desired_capabilities=iOS_capabilities
        )
        driver.implicitly_wait(10)
        driver.start_session(iOS_capabilities)
        return driver

# # Run standard unittest base.
# class AppiumDriverTests(unittest.TestCase):
#     driver = None
#
#     def setUp(self):
#         os.system('appium &')
#         driver = webdriver.Remote(
#             command_executor=EXECUTOR,
#             desired_capabilities=iOS_capabilities
#         )
#         driver.implicitly_wait(10)
#         driver.start_session(iOS_capabilities)
#
#
#     def test_should_create_and_destroy_ios_session(self):
#         app_element = self.driver.find_element_by_class_name('XCUIElementTypeApplication')
#         app_element_name = app_element.get_attribute('name')
#
#         self.assertEquals('TestApp', app_element_name)
#         self.driver.quit()
#
#         with self.assertRaises(InvalidSessionIdException) as excinfo:
#             self.driver.title
#         self.assertEquals('A session is either terminated or not started', excinfo.exception.msg)
