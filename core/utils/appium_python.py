import os

import psutil
import pytest
import datetime

from appium import webdriver
from selenium.common.exceptions import InvalidSessionIdException

from core.settings import Settings


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


class AppiumDriver(object):
    def __init__(self, capabilities):
        psutil.Popen("appium --port 4723", cwd=Settings.TEST_RUN_HOME, shell=True, stdin=None, stdout=None,
                     stderr=None, close_fds=True)
        self.capabilities = capabilities
        self.executor = 'http://127.0.0.1:4723/wd/hub'
        self.driver = webdriver.Remote(self.executor, capabilities)
