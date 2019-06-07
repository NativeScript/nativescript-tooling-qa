import os
import time

from parameterized import parameterized
from selenium.common.exceptions import NoSuchElementException

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.chrome.chrome import Chrome
from products.nativescript.market_helpers import Market
from products.nativescript.preview_helpers import Preview


# noinspection PyUnusedLocal
class PlaygroundMarketSamples(TnsRunTest):
    chrome = None
    app_name = Settings.AppName.DEFAULT
    is_ios_fail = None
    test_data = Market.get_data_market()

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
        retries = 1
        while retries >= 0:
            print text
            self.chrome = Chrome()
            link, is_slow = PlaygroundMarketSamples.get_link(self.chrome, url)
            original_name = name.replace("_", " ").encode("utf8")
            if link == "":
                Log.info('No Playground URL found !!!')
                data = {"name": original_name, "ios": "False", "android": "False", "flavor": str(flavor),
                        "timeout": "True", "slow": "True"}
                retries -= 1
            else:
                image_name = '{0}_{1}.png'.format(name.encode("utf8"), str(Platform.ANDROID))
                Preview.run_url(url=link, device=self.emu)
                # emulator_result = PlaygroundMarketSamples.wait_for_text(self.emu, text)
                emulator_result = PlaygroundMarketSamples.get_error(self.chrome)
                # if not emulator_result:
                is_android_fail = emulator_result > 0
                if is_android_fail:
                    self.emu.get_screen(os.path.join(Settings.TEST_OUT_IMAGES, image_name))
                if Settings.HOST_OS == OSType.OSX:
                    image_name = '{0}_{1}.png'.format(name.encode("utf8"), str(Platform.IOS))

                    if self.is_ios_fail:
                        Log.info(' Installing Preview app on iOS ...')
                        Preview.install_preview_app_no_unpack(self.sim, Platform.IOS)

                    Preview.run_url(url=link, device=self.sim)
                    Log.info(' Waiting iOS app to load...')
                    time.sleep(10)
                    Preview.dismiss_simulator_alert()
                    # simulator_result = PlaygroundMarketSamples.wait_for_text(self.sim, text)
                    simulator_result = PlaygroundMarketSamples.get_error(self.chrome, emulator_result)
                    is_app_active = Preview.is_running_on_ios(self.sim, Settings.Packages.PREVIEW_APP_ID)
                    # if not simulator_result:
                    self.is_ios_fail = simulator_result > 0 or not is_app_active
                    os.environ["is_ios_fail"] = str(self.is_ios_fail)

                    if self.is_ios_fail:
                        self.sim.get_screen(os.path.join(Settings.TEST_OUT_IMAGES, image_name))

                ios = str(not self.is_ios_fail)
                android = str(not is_android_fail)
                data = {"name": original_name, "ios": ios, "android": android, "flavor": str(flavor),
                        "slow": str(is_slow)}
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
        exceptions = 0
        timeout = 20  # In seconds
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
