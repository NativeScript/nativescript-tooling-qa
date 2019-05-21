import os
import time

from nose_parameterized import parameterized

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.chrome.chrome import Chrome
from products.nativescript.preview_helpers import Preview


# noinspection PyUnusedLocal
class PlaygroundDocSamples(TnsRunTest):
    chrome = None
    app_name = Settings.AppName.DEFAULT

    test_data = [
        ['getting_started_ng', 'template=play-ng&tutorial=getting-started-ng', 'Play with NativeScript!'],
        ['getting_started_js', 'template=groceries-js&tutorial=groceries-js', 'hello world'],
        ['animate_background_color', 'template=play-tsc&id=aLjBQg', 'Tap to animate'],
        ['animate_position', 'template=play-tsc&id=egSanf', 'Tap to animate'],
        ['hub_modal', 'template=play-ng&id=MN31oP', 'Search'],
        ['hub', 'template=play-ng&id=lpCc2k', 'Search'],
        ['animation', 'template=play-tsc&id=h6g8J8', 'Run animation'],
        ['keyframes_animation', 'template=play-tsc&id=tQRe9Q', 'Home'],
        ['navigation', 'template=play-tsc&id=o41kGU', 'Navigate To Item'],
        ['navigate_item_page', 'template=play-tsc&id=qk6ACL', 'Featured'],
        ['layouts', 'template=play-tsc&id=obk2gB', 'Button'],
        ['stack_layout', 'template=play-tsc&id=JY218G', 'Play with NativeScript!'],
        ['dialogs', 'template=play-ng&id=zJ51uY', 'Confirm'],
        ['share_this', 'template=play-js&id=RTWLSH', 'Share This!'],
        ['action_bar', 'template=play-tsc&id=IrIZ5I', 'Home Alone?'],
        ['events-js', 'template=play-js&id=kIs7uK', 'Events'],
        ['events-ts', 'template=play-tsc&id=8Rhm07', 'Events'],
        ['is_user_iteraction_enabled', 'template=play-tsc&id=6c9GA0', 'TAP']
    ]

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        Preview.install_preview_app(cls.emu, Platform.ANDROID)
        if Settings.HOST_OS is OSType.OSX:
            Preview.install_preview_app(cls.sim, Platform.IOS)
            Preview.install_playground_app(cls.sim, Platform.IOS)

    def setUp(self):
        TnsRunTest.setUp(self)
        self.chrome = Chrome()

    def tearDown(self):
        self.chrome.kill()
        TnsRunTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsRunTest.tearDownClass()

    @parameterized.expand(test_data)
    def test(self, name, url, text):
        link = PlaygroundDocSamples.get_link(self.chrome, url)
        image_name = '{0}_{1}.png'.format(name, str(Platform.ANDROID))
        Preview.run_url(url=link, device=self.emu)
        self.emu.wait_for_text(text=text)
        self.emu.get_screen(os.path.join(Settings.TEST_OUT_IMAGES, image_name))
        if Settings.HOST_OS == OSType.OSX:
            image_name = '{0}_{1}.png'.format(name, str(Platform.IOS))
            Preview.run_url(url=link, device=self.sim)
            time.sleep(2)
            Preview.dismiss_simulator_alert()
            self.sim.wait_for_text(text=text)
            self.sim.get_screen(os.path.join(Settings.TEST_OUT_IMAGES, image_name))

    # noinspection PyBroadException
    @staticmethod
    def get_link(chrome, url):
        url = 'https://play.nativescript.org/?{0}&debug=true'.format(url)
        chrome.open(url)
        link = chrome.driver.find_element_by_xpath("//span[contains(.,'nsplay://boot')]").text
        return link
