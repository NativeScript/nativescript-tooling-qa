import os

from core.base_test.tns_run_android_test import TnsRunAndroidTest
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder
from data.sync.hello_world_js import sync_hello_world_js, run_hello_world_js_ts
from products.nativescript.tns import Tns
from products.nativescript.tns_paths import TnsPaths

Settings.Emulators.DEFAULT = Settings.Emulators.EMU_API_28


class TnsRunJSTests(TnsRunAndroidTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = TnsPaths.get_app_path(app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)

    @classmethod
    def setUpClass(cls):
        TnsRunAndroidTest.setUpClass()

        # Create app
        Tns.create(app_name=cls.app_name, template='tns-template-hello-world@6.0')

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsRunAndroidTest.setUp(self)

        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        source_src = os.path.join(self.target_project_dir, 'app')
        target_src = os.path.join(self.source_project_dir, 'app')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)

    @classmethod
    def tearDownClass(cls):
        TnsRunAndroidTest.tearDownClass()

    def test_100_run_android(self):
        """
            Run android, verify app is built with api28 and verify livesync
        """
        # Run app and verify on emulator
        sync_hello_world_js(self.app_name, Platform.ANDROID, self.emu, default_andr_sdk='28')

    def test_200_run_android_release_snapshot(self):
        """
            Run android, verify app is built with api28
        """
        # Run app and verify on emulator
        run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu, default_andr_sdk='28',
                              release=True, snapshot=True)
