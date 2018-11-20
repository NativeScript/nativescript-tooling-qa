import os

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder
from data.apps import Apps
from products.angular.ng import NG, NS_SCHEMATICS
from products.nativescript.tns import Tns
from products.nativescript.tns_assert import TnsAssert


# noinspection PyMethodMayBeStatic
class SmokeTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_folder = os.path.join(Settings.TEST_RUN_HOME, app_name)
    emu = None
    sim = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

    def setUp(self):
        TnsTest.setUp(self)
        Folder.clean(self.app_folder)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_001_simple(self):
        SmokeTests.create_build_run(shared=False, sample=False)

    def test_002_simple_with_sample(self):
        SmokeTests.create_build_run(shared=False, sample=True)

    def test_003_shared(self):
        SmokeTests.create_build_run(shared=True, sample=False)

    def test_004_shared_with_sample(self):
        SmokeTests.create_build_run(shared=True, sample=True)

    def test_300_help_ng_new(self):
        output = NG.exec_command('new --collection={0} --help'.format(NS_SCHEMATICS)).output
        assert '--sample' in output
        assert 'Specifies whether a sample master detail should be generated' in output
        assert '--shared' in output
        assert 'Specifies whether to generate a shared project or a {N} only' in output
        assert '--source-dir (-sd)' in output
        assert 'The path of the source directory' in output
        assert '--style' in output
        assert 'The file extension to be used for style files. Supported are css and scss' in output
        assert '--theme' in output
        assert 'Specifies whether the {N} theme for styling should be included' in output
        assert '--webpack' in output
        assert 'Specifies whether the new application has webpack set up' in output

    @staticmethod
    def create_build_run(shared=True, sample=True):
        # Create shared project with sample data
        NG.new(collection=NS_SCHEMATICS, project=SmokeTests.app_name, shared=shared, sample=sample)
        TnsAssert.created(app_name=SmokeTests.app_name, app_data=Apps.SHEMATICS_SHARED)

        # Build in release
        Tns.build(app_name=SmokeTests.app_name, platform=Platform.ANDROID, release=True,
                  bundle=True, aot=True, uglify=True, snapshot=True)
        if Settings.HOST_OS is OSType.OSX:
            Tns.build(app_name=SmokeTests.app_name, platform=Platform.IOS, release=True, for_device=True,
                      bundle=True, aot=True, uglify=True)

        # Run and sync changes
        Tns.run(app_name=SmokeTests.app_name, platform=Platform.ANDROID, bundle=True)
        SmokeTests.emu.wait_for_text(texts=Apps.SHEMATICS_SHARED.texts, timeout=30)
        if Settings.HOST_OS is OSType.OSX:
            Tns.run(app_name=SmokeTests.app_name, platform=Platform.IOS, bundle=True)
            SmokeTests.sim.wait_for_text(texts=Apps.SHEMATICS_SHARED.texts, timeout=30)
