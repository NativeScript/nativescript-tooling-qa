import os
import time

from nose_parameterized import parameterized

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.chrome import Chrome
from products.nativescript.preview_helpers import Preview
from products.nativescript.market_helpers import Market
from selenium.common.exceptions import NoSuchElementException


# noinspection PyUnusedLocal
class PlaygroundMarketSamples(TnsRunTest):
    chrome = None
    app_name = Settings.AppName.DEFAULT
    is_ios_fail = None
    test_data = Market.get_data()

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
        self.chrome = Chrome()
        self.is_ios_fail = os.environ.get('is_ios_fail') == 'True'

    def tearDown(self):
        self.chrome.kill()
        TnsRunTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsRunTest.tearDownClass()

    @parameterized.expand(test_data)
    def test(self, name, url, text, flavor):
        print text
        link = PlaygroundMarketSamples.get_link(self.chrome, url)
        original_name = str(name).replace("_", " ")
        if link == "":
            data = {"name": original_name, "ios": "False", "android": "False", "flavor": str(flavor)}
            Market.preserve_data(data)
        else:
            image_name = '{0}_{1}.png'.format(name, str(Platform.ANDROID))
            Preview.run_url(url=link, device=self.emu)
            # emulator_result = PlaygroundMarketSamples.wait_for_text(self.emu, text)
            emulator_result = PlaygroundMarketSamples.get_error(self.chrome)
            # if not emulator_result:
            is_android_fail = emulator_result > 0
            if is_android_fail:
                self.emu.get_screen(os.path.join(Settings.TEST_OUT_IMAGES, image_name))
            if Settings.HOST_OS == OSType.OSX:
                image_name = '{0}_{1}.png'.format(name, str(Platform.IOS))
                if self.is_ios_fail:
                    Log.info(' Installing Preview app on iOS ...')
                    Preview.install_preview_app_no_unpack(self.sim, Platform.IOS)
                Preview.run_url(url=link, device=self.sim)
                Log.info(' Waiting iOS app to load...')
                time.sleep(10)
                Preview.dismiss_simulator_alert()
                # simulator_result = PlaygroundMarketSamples.wait_for_text(self.sim, text)
                simulator_result = PlaygroundMarketSamples.get_error(self.chrome, emulator_result)
                # if not simulator_result:
                self.is_ios_fail = simulator_result > 0
                os.environ["is_ios_fail"] = str(self.is_ios_fail)
                if self.is_ios_fail:
                    self.sim.get_screen(os.path.join(Settings.TEST_OUT_IMAGES, image_name))

            ios = str(not self.is_ios_fail)
            android = str(not is_android_fail)
            data = {"name": original_name, "ios": ios, "android": android, "flavor": str(flavor)}
            Market.preserve_data(data)

    # noinspection PyBroadException
    @staticmethod
    def get_link(chrome, url):
        url = '{0}&debug=true'.format(url)
        chrome.open(url)
        link = ""
        for _ in range(1):
            try:
                Log.info('Searching for QR url ...')
                link = chrome.driver.find_element_by_xpath("//span[contains(.,'nsplay://boot')]").text
            except NoSuchElementException:
                Log.info('No Playground URL found ...')
            if "nsplay" in link:
                break
            time.sleep(1)
        return link

    @staticmethod
    def get_error(chrome, previous_errors=0):
        exceptions = 0
        for _ in range(2 + previous_errors):
            Log.info(' Searching for exception ...')
            elements = chrome.driver.find_elements_by_xpath("//span[contains(.,'Exception')]")
            exceptions = len(elements) - previous_errors
            if exceptions > 0:
                error = elements[previous_errors].text
                print error
                break
            else:
                time.sleep(1)
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
