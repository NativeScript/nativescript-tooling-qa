
import os

from nose_parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import File
from data.apps import Apps
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
from products.nativescript.tns_paths import TnsPaths


class CreateTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    NODE_MODULES = 'node_modules'
    TNS_MODULES = os.path.join(NODE_MODULES, 'tns-core-modules')
    HOOKS = 'hooks'
    PLATFORM_IOS = os.path.join('platforms', 'ios/')
    PLATFORM_ANDROID = os.path.join('platforms', 'android/')
    PLATFORM_ANDROID_BUILD = os.path.join(PLATFORM_ANDROID, 'app', 'build')
    PLATFORM_ANDROID_APK_PATH = os.path.join(PLATFORM_ANDROID_BUILD, 'outputs', 'apk')
    PLATFORM_ANDROID_APK_RELEASE_PATH = os.path.join(PLATFORM_ANDROID_BUILD, 'outputs', 'apk', 'release')
    PLATFORM_ANDROID_APK_DEBUG_PATH = os.path.join(PLATFORM_ANDROID_BUILD, 'outputs', 'apk', 'debug')
    PLATFORM_ANDROID_SRC_MAIN_PATH = os.path.join(PLATFORM_ANDROID, 'app', 'src', 'main/')
    PLATFORM_ANDROID_APP_PATH = os.path.join(PLATFORM_ANDROID_SRC_MAIN_PATH, 'assets', 'app/')
    PLATFORM_ANDROID_NPM_MODULES_PATH = os.path.join(PLATFORM_ANDROID_APP_PATH, 'tns_modules/')
    PLATFORM_ANDROID_TNS_MODULES_PATH = os.path.join(PLATFORM_ANDROID_NPM_MODULES_PATH, 'tns-core-modules/')

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(app_name=Settings.AppName.DEFAULT, app_data=Apps.HELLO_WORLD_JS, update=False)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_100_plugin_add_after_platform_add_android(self):
        result = Tns.plugin_add(plugin_name='tns-plugin', path=Settings.AppName.DEFAULT)
        # Tns.plugin_remove(plugin_name='nativescript-camera', path=Settings.AppName.DEFAULT)
        assert "Successfully installed plugin tns-plugin" in result.output
        assert File.exists(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'tns-plugin', 'index.js'))
        assert File.exists(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'tns-plugin', 'package.json'))

        result = File.read(os.path.join(Settings.AppName.DEFAULT, 'package.json'))
        assert "org.nativescript.TestApp" in result.output
        assert "dependencies" in result.output
        assert "tns-plugin" in result.output

    def test_101_plugin_add_after_platform_add_android(self):
        Tns.plugin_add(plugin_name='tns-plugin', path=Settings.AppName.DEFAULT, verify=False)
        Tns.prepare_android(app_name=Settings.AppName.DEFAULT)
        apk = TnsPaths.get_apk(app_name=Settings.AppName.DEFAULT)
        assert File.exists(os.path.join(Settings.AppName.DEFAULT, self.PLATFORM_ANDROID_APK_DEBUG_PATH))
        assert File.exists(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'tns-plugin', 'index.js'))
        assert File.exists(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'tns-plugin', 'package.json'))


