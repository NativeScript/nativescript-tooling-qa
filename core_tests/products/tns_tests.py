import os

from nose.tools import timed

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File
from core.utils.wait import Wait
from products.nativescript.tns import Tns
from products.nativescript.tns_helpers import TnsHelpers


class TnsTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_folder = os.path.join(Settings.TEST_RUN_HOME, app_name)
    emu = None
    sim = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(app_name=cls.app_name)
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

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
        result = Tns.run_android(app_name=self.app_name, device=self.emu.id, wait=False)

        # Verify result object
        assert result.complete is False, 'tns run with wait false should not complete after command above is executed.'
        assert result.exit_code is None, 'tns run with wait false is hav eno exit code since it is not complete.'
        assert result.log_file is not None, 'stdout and stderr should be redirected to file.'

        # Wait until app is build and installed.
        texts = ['Project successfully built', 'Successfully installed']
        TnsHelpers.wait_for_log(result.log_file, texts)

    @timed(300)
    def test_002_tns_run_android_with_justlaunch(self):
        result = Tns.run_android(app_name=self.app_name, device=self.emu.id, justlaunch=True, wait=True)
        assert result.complete is True, 'tns run with --justlauch and wait=true should wait until command is executed.'
        assert result.exit_code == 0, 'tns run should be successful.'
        assert 'Successfully synced application' in result.output
