from nose_parameterized import parameterized

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.chrome import Chrome
from products.nativescript.preview_helpers import Preview


# noinspection PyUnusedLocal
class PlaygroundDocSamples(TnsRunTest):
    chrome = None
    app_name = Settings.AppName.DEFAULT

    test_data = [
        # ['t01', 'template=play-ng&tutorial=getting-started-ng'],
        # ['t02', 'template=groceries-js&tutorial=groceries-js'],
        ['t03', 'template=play-tsc&id=aLjBQg'],
        ['t04', 'template=play-tsc&id=egSanf'],
        ['t05', 'template=play-ng&id=MN31oP'],
        ['t06', 'template=play-ng&id=lpCc2k'],
        ['t07', 'template=play-tsc&id=h6g8J8'],
        ['t08', 'template=play-tsc&id=tQRe9Q'],
        ['t09', 'template=play-tsc&id=o41kGU'],
        ['t10', 'template=play-tsc&id=qk6ACL'],
        ['t11', 'template=play-tsc&id=obk2gB'],
        ['t12', 'template=play-tsc&id=JY218G'],
        ['t13', 'template=play-js&id=RTWLSH'],
        ['t14', 'template=play-tsc&id=IrIZ5I'],
        ['t15', 'template=play-js&id=kIs7uK'],
        ['t16', 'template=play-tsc&id=8Rhm07'],
        ['t17', 'template=play-tsc&id=6c9GA0'],
        ['t18', 'template=play-ng&id=zJ51uY']
    ]

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        Preview.get_app_packages()
        Preview.install_preview_app(cls.emu, Platform.ANDROID)
        if Settings.HOST_OS is OSType.OSX:
            Preview.install_preview_app(cls.sim, Platform.IOS)
            Preview.install_playground_app(cls.sim, Platform.IOS)
        cls.chrome = Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.chrome.kill()
        TnsRunTest.tearDownClass()

    @parameterized.expand(test_data)
    def test(self, name, url):
        link = PlaygroundDocSamples.get_link(self.chrome, url)
        Preview.run_app(url=link, device_id=self.emu.id, platform=Platform.ANDROID)
        if Settings.HOST_OS == OSType.OSX:
            Preview.run_app(url=link, device_id=self.emu.id, platform=Platform.IOS)

    # noinspection PyBroadException
    @staticmethod
    def get_link(chrome, url):
        url = 'https://play.nativescript.org/?{0}'.format(url)
        chrome.open(url)
        link = chrome.driver.find_element_by_xpath("//span[contains(.,'nsplay://boot')]").text
        return link
