import os

from core.base_test.base_test import BaseTest
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
class SmokeTests(BaseTest):
    app_name = Settings.AppName.DEFAULT
    app_folder = os.path.join(Settings.TEST_RUN_HOME, app_name)
    emu = None
    sim = None

    @classmethod
    def setUpClass(cls):
        BaseTest.setUpClass()
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

    def setUp(self):
        BaseTest.setUp(self)
        Folder.clean(self.app_folder)

    def tearDown(self):
        BaseTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        BaseTest.tearDownClass()

    def test_001_simple(self):
        # Create simple NS app and verify it is created properly
        NG.new(collection=NS_SCHEMATICS, project=self.app_name, shared=False, sample=False)
        TnsAssert.created(app_name=self.app_name, app_data=Apps.SHEMATICS_NS)

        # Build in release
        Tns.build(app_name=self.app_name, platform=Platform.ANDROID, release=True,
                  bundle=True, aot=True, uglify=True, snapshot=True)
        if Settings.HOST_OS is OSType.OSX:
            Tns.build(app_name=self.app_name, platform=Platform.IOS, release=True, for_device=True,
                      bundle=True, aot=True, uglify=True)

        # Run and sync changes
        Tns.run(app_name=self.app_name, platform=Platform.ANDROID, bundle=True)
        self.emu.wait_for_text(texts=Apps.SHEMATICS_NS.texts, timeout=300)
        Tns.kill()
        if Settings.HOST_OS is OSType.OSX:
            Tns.run(app_name=self.app_name, platform=Platform.IOS, bundle=True)
            self.sim.wait_for_text(texts=Apps.SHEMATICS_NS.texts, timeout=300)

    def test_002_simple_with_sample(self):
        # Create NS with sample data
        NG.new(collection=NS_SCHEMATICS, project=self.app_name, shared=False, sample=True)
        TnsAssert.created(app_name=self.app_name, app_data=Apps.SHEMATICS_NS)

        # Build in release
        Tns.build(app_name=self.app_name, platform=Platform.ANDROID, release=True,
                  bundle=True, aot=True, uglify=True, snapshot=True)
        if Settings.HOST_OS is OSType.OSX:
            Tns.build(app_name=self.app_name, platform=Platform.IOS, release=True, for_device=True,
                      bundle=True, aot=True, uglify=True)

        # Run and sync changes
        Tns.run(app_name=self.app_name, platform=Platform.ANDROID, bundle=True)
        self.emu.wait_for_text(texts=Apps.SHEMATICS_NS.texts, timeout=30)
        if Settings.HOST_OS is OSType.OSX:
            Tns.run(app_name=self.app_name, platform=Platform.IOS, bundle=True)
            self.sim.wait_for_text(texts=Apps.SHEMATICS_NS.texts, timeout=30)

    def test_003_shared(self):
        # Create simple shared project
        NG.new(collection=NS_SCHEMATICS, project=self.app_name, shared=True, sample=False)
        TnsAssert.created(app_name=self.app_name, app_data=Apps.SHEMATICS_SHARED)

        # Build in release
        Tns.build(app_name=self.app_name, platform=Platform.ANDROID, release=True,
                  bundle=True, aot=True, uglify=True, snapshot=True)
        if Settings.HOST_OS is OSType.OSX:
            Tns.build(app_name=self.app_name, platform=Platform.IOS, release=True, for_device=True,
                      bundle=True, aot=True, uglify=True)

        # Run and sync changes
        Tns.run(app_name=self.app_name, platform=Platform.ANDROID, bundle=True)
        self.emu.wait_for_text(texts=Apps.SHEMATICS_SHARED.texts, timeout=30)
        if Settings.HOST_OS is OSType.OSX:
            Tns.run(app_name=self.app_name, platform=Platform.IOS, bundle=True)
            self.sim.wait_for_text(texts=Apps.SHEMATICS_SHARED.texts, timeout=30)

    def test_004_shared_with_sample(self):
        # Create shared project with sample data
        NG.new(collection=NS_SCHEMATICS, project=self.app_name, shared=True, sample=True)
        TnsAssert.created(app_name=self.app_name, app_data=Apps.SHEMATICS_SHARED)

        # Build in release
        Tns.build(app_name=self.app_name, platform=Platform.ANDROID, release=True,
                  bundle=True, aot=True, uglify=True, snapshot=True)
        if Settings.HOST_OS is OSType.OSX:
            Tns.build(app_name=self.app_name, platform=Platform.IOS, release=True, for_device=True,
                      bundle=True, aot=True, uglify=True)

        # Run and sync changes
        Tns.run(app_name=self.app_name, platform=Platform.ANDROID, bundle=True)
        self.emu.wait_for_text(texts=Apps.SHEMATICS_SHARED.texts, timeout=30)
        if Settings.HOST_OS is OSType.OSX:
            Tns.run(app_name=self.app_name, platform=Platform.IOS, bundle=True)
            self.sim.wait_for_text(texts=Apps.SHEMATICS_SHARED.texts, timeout=30)

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
