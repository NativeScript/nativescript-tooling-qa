import os

from nose.tools import timed

from core.base_test.tns_test import TnsTest
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from data.apps import Apps
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


class TnsTests(TnsTest):
    app_folder = os.path.join(Settings.TEST_RUN_HOME, Settings.AppName.DEFAULT)

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(app_name=Settings.AppName.DEFAULT)
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)

    def setUp(self):
        TnsTest.setUp(self)

    def tearDown(self):
        Tns.kill()
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    @timed(300)
    def test_001_tns_run_android(self):
        result = Tns.run_android(app_name=Settings.AppName.DEFAULT, device=self.emu.id, wait=False)

        # Verify result object
        assert result.complete is False, 'tns run with wait false should not complete after command above is executed.'
        assert result.exit_code is None, 'tns run with wait false is hav eno exit code since it is not complete.'
        assert result.log_file is not None, 'stdout and stderr should be redirected to file.'

        # Verify console logs of `tns run` command
        plugins = ['nativescript-theme-core', 'tns-core-modules', 'tns-core-modules-widgets']
        messages = TnsLogs.run_messages(app_name=Settings.AppName.DEFAULT,
                                        platform=Platform.ANDROID,
                                        run_type=RunType.FIRST_TIME,
                                        plugins=plugins)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=messages, timeout=300)

        # Verify app looks ok
        for text in Apps.HELLO_WORLD_JS.texts:
            self.emu.wait_for_text(text=text)

    @timed(300)
    def test_002_tns_run_android_with_justlaunch(self):
        result = Tns.run_android(app_name=Settings.AppName.DEFAULT, device=self.emu.id, just_launch=True, wait=True)
        assert result.complete is True, 'tns run with --justlauch and wait=true should wait until command is executed.'
        assert result.exit_code == 0, 'tns run should be successful.'
        assert 'Successfully synced application' in result.output
