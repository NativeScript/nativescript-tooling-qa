import os
import sys
import time

from parameterized import parameterized
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.chrome.chrome import Chrome
from products.nativescript.market_helpers import Market
from products.nativescript.preview_helpers import Preview


def custom_name_func(testcase_func, param_num, param):
    return "%s_%s_%s" % (testcase_func.__name__, param_num, param.args[0])


# noinspection PyUnusedLocal
class PlaygroundMarketSamples(TnsRunTest):
    chrome = None
    app_name = Settings.AppName.DEFAULT
    is_ios_fail = None
    test_data = Market.get_data_market()
    range = sys.argv[-1]
    if "samples=" in range:
        range_array = str(range).replace("samples=", "").split("-")
        start = int(range_array[0])
        end = int(range_array[1])
        test_data = test_data[start:end]
        Log.info("====== Running test for samples in the range {}-{} ======".format(start, end))
    # test_data = [x for x in test_data1 if u'Getting_a_User\'s_Current_Location' in x]
    # print test_data
    # test_data = [
    #     ['getting_started_ng', 'https://play.nativescript.org/?template=play-ng&id=2OkUP6', 'Play', 'ng'],
    #     ['getting_started_ng', 'https://play.nativescript.org/?template=play-tsc&id=TcHeUQ&v=10', 'Play', 'ng']
    # ]

    @classmethod
    def setUpClass(cls):
        Market.remove_results_file()
        Settings.Emulators.DEFAULT = Settings.Emulators.EMU_API_28
        TnsRunTest.setUpClass()
        Preview.install_preview_app(cls.emu, Platform.ANDROID)
        if Settings.HOST_OS is OSType.OSX:
            Preview.install_preview_app(cls.sim, Platform.IOS)
            Preview.install_playground_app(cls.sim, Platform.IOS)

    def setUp(self):
        TnsRunTest.setUp(self)
        self.is_ios_fail = os.environ.get('is_ios_fail') == 'True'

    def tearDown(self):
        self.chrome.kill()
        TnsRunTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsRunTest.tearDownClass()

    @parameterized.expand(test_data)
    def test(self, name, url, text, flavor):
        Log.info(text)
        retries = 1
        original_name = name.replace("_", " ").encode("utf8")
        data = {"name": original_name, "ios": "False", "android": "False", "flavor": str(flavor),
                "timeout": "False", "slow": "False"}
        is_android_fail = True
        is_ios_fail = True

        while retries >= 0:
            # =====================Android RUN========================
            if is_android_fail:
                self.chrome = Chrome()
                link, is_slow = PlaygroundMarketSamples.get_link(self.chrome, url)
                if link == "":
                    Log.info('No Playground URL found in Android stage !!!')
                    data["timeout"] = "True"
                    data["slow"] = "True"
                    retries -= 1
                    continue

                Log.info('Testing Android !!!')
                image_name = '{0}_{1}.png'.format(name.encode("utf8"), str(Platform.ANDROID))
                Preview.run_url(url=link, device=self.emu)
                Log.info(' Waiting Android app to load...')
                time.sleep(10)
                PlaygroundMarketSamples.verify_device_is_connected(self.chrome, "Android SDK built")
                emulator_result = PlaygroundMarketSamples.get_error(self.chrome)
                is_android_fail = emulator_result > 0
                android = str(not is_android_fail)
                data["android"] = android
                data["slow"] = str(is_slow)

                if is_android_fail:
                    self.emu.get_screen(os.path.join(Settings.TEST_OUT_IMAGES, image_name))
                self.chrome.kill()

            # =====================iOS RUN========================
            if Settings.HOST_OS == OSType.OSX and is_ios_fail:
                image_name = '{0}_{1}.png'.format(name.encode("utf8"), str(Platform.IOS))

                if self.is_ios_fail:
                    Log.info(' Installing Preview app on iOS ...')
                    Preview.install_preview_app_no_unpack(self.sim, Platform.IOS)

                self.chrome = Chrome()
                link, is_slow = PlaygroundMarketSamples.get_link(self.chrome, url)
                if link == "":
                    Log.info('No Playground URL found in iOS stage !!!')
                    data["timeout"] = "True"
                    data["slow"] = "True"
                    retries -= 1
                    continue

                Log.info('Testing iOS !!!')
                Preview.run_url(url=link, device=self.sim)
                if "test_0_" in self._testMethodName or "test_000_" in self._testMethodName:
                    time.sleep(10)
                    PlaygroundMarketSamples.close_popup(self.sim)
                Log.info(' Waiting iOS app to load...')
                Preview.dismiss_simulator_alert()
                time.sleep(10)
                PlaygroundMarketSamples.verify_device_is_connected(self.chrome, self.sim.name)
                Preview.dismiss_simulator_alert()

                if "test_0_" in self._testMethodName or "test_000_" in self._testMethodName:
                    PlaygroundMarketSamples.close_popup(self.sim)

                PlaygroundMarketSamples.close_permissions_windows_ios(name, self.sim)
                simulator_result = PlaygroundMarketSamples.get_error(self.chrome)
                is_app_active = Preview.is_running_on_ios(self.sim, Settings.Packages.PREVIEW_APP_ID)
                self.is_ios_fail = simulator_result > 0 or not is_app_active
                is_ios_fail = self.is_ios_fail
                os.environ["is_ios_fail"] = str(self.is_ios_fail)

                if self.is_ios_fail:
                    self.sim.get_screen(os.path.join(Settings.TEST_OUT_IMAGES, image_name))

                ios = str(not self.is_ios_fail)
                data["ios"] = ios
                data["slow"] = str(is_slow)

            if self.is_ios_fail is False and is_android_fail is False:
                break
            retries -= 1
            self.tearDown()

        Market.preserve_data(data)

    # noinspection PyBroadException
    @staticmethod
    def get_link(chrome, url):
        url = '{0}&debug=true'.format(url)
        chrome.open(url)
        link = ""
        timeout = 60  # In seconds
        slow = False
        end_time = time.time() + timeout
        while end_time > time.time():
            try:
                Log.info('Searching for QR url ...')
                link = chrome.driver.find_element_by_xpath("//span[contains(.,'nsplay://boot')]").text
            except NoSuchElementException:
                Log.info('No Playground URL element found ...')
            if "nsplay" in link:
                Log.info('Url link found ...')
                if (end_time - time.time()) < 35:
                    slow = True
                break
        return link, slow

    @staticmethod
    def get_error(chrome, previous_errors=0):
        PlaygroundMarketSamples.open_device_logs(chrome)
        exceptions = 0
        timeout = 10  # In seconds
        end_time = time.time() + timeout
        while end_time > time.time():
            Log.info(' Searching for exception ...')
            elements = chrome.driver.find_elements_by_xpath("//span[contains(.,'Exception')]")
            exceptions = len(elements) - previous_errors
            if exceptions > 0:
                error = elements[previous_errors].text
                print error
                break
        return exceptions

    @staticmethod
    def wait_for_text(emu, text, timeout=20, retry_delay=1):
        t_end = time.time() + timeout
        found = False
        error_msg = '{0} NOT found on {1}.'.format(text, emu.name)
        found_msg = '{0} found on {1}.'.format(text, emu.name)
        while time.time() < t_end:
            if emu.is_text_visible(text=text):
                found = True
                Log.info(found_msg)
                break
            else:
                Log.info(error_msg + ' Waiting ...')
                time.sleep(retry_delay)
        if not found:
            text = emu.get_text()
            Log.info('Current text: {0}{1}'.format(os.linesep, text))
        return found

    @staticmethod
    def close_permissions_windows_ios(name, sim):
        samples = ['Instagram_Clone_with_Image_Filters']
        iterations = 1
        if name in samples:
            is_ok_button_visible = PlaygroundMarketSamples.wait_for_text(sim, "OK", 10)
            while is_ok_button_visible:
                iterations = iterations + 1
                Preview.dismiss_simulator_alert()
                time.sleep(1)
                is_ok_button_visible = PlaygroundMarketSamples.wait_for_text(sim, "OK", 5)
                if iterations == 5:
                    break

    @staticmethod
    def verify_device_is_connected(chrome, device, timeout=15):
        PlaygroundMarketSamples.close_cookie_alert(chrome)
        Log.info("Check device in Playground")
        t_end = time.time() + timeout
        while time.time() < t_end:
            try:
                chrome.driver.find_elements_by_xpath("//span[contains(.,'Devices')]")[0].click()
                Log.info('Devices button clicked.')
                break
            except ElementClickInterceptedException:
                Log.info('Unable to click Devices button!')
                time.sleep(3)
        devices = chrome.driver.find_elements_by_class_name('device-name')
        try:
            if devices:
                device_name = devices[0].text
                if device not in device_name:
                    Log.info("Searched device not found !!! Actual: " + str(device_name) + " Expected: " + device)
            else:
                Log.info("No device has been found to be attached !!!")
        except StaleElementReferenceException:
            Log.info('Device name element has been removed from the DOM!!!')

    @staticmethod
    def open_device_logs(chrome, timeout=5):
        Log.info("Open device Logs")
        t_end = time.time() + timeout
        while time.time() < t_end:
            try:
                chrome.driver.find_elements_by_xpath("//span[contains(.,'Device Logs')]")[0].click()
                Log.info('Device Log opened.')
                break
            except ElementClickInterceptedException:
                Log.info('Unable to click Device Log!')
                time.sleep(2)

    @staticmethod
    def close_popup(device, timeout=10, button_text="Open"):
        if PlaygroundMarketSamples.wait_for_text(device, button_text, timeout):
            device.click(text=button_text)
            # Preview.dismiss_simulator_alert()

    @staticmethod
    def close_cookie_alert(chrome):
        Log.info("Close cookie alert.")
        accept_cookies = chrome.driver.find_elements_by_xpath("//button[contains(.,'Accept Cookies')]")
        if accept_cookies:
            accept_cookies[0].click()
