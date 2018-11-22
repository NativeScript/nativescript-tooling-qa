import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.enums.styling_type import StylingType
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder
from data.apps import Apps
from data.const import Colors
from products.angular.ng import NG, NS_SCHEMATICS
from products.nativescript.app import App
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

    def test_010_shared(self):
        SmokeTests.create_build_run(shared=True, sample=False)

    def test_100_shared_with_sample(self):
        SmokeTests.create_build_run(shared=True, sample=True)

    def test_200_simple_no_theme(self):
        SmokeTests.create_build_run(shared=False, theme=False)

    def test_201_shared_with_sass(self):
        SmokeTests.create_build_run(shared=False, style=StylingType.SCSS)

    def test_202_shared_with_custom_sourcedir_and_prefix(self):
        SmokeTests.create_build_run(shared=False, prefix='myapp', source_dir='mysrc')

    def test_300_simple_no_webpack(self):
        SmokeTests.create_build_run(shared=False, webpack=False)

    @unittest.skip('Ignore because of https://github.com/NativeScript/nativescript-schematics/issues/157')
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
    def create_build_run(shared=True, sample=False, theme=True, style=StylingType.CSS, prefix=None, source_dir=None,
                         webpack=True):

        app_data = Apps.SHEMATICS_NS
        if shared:
            app_data = Apps.SHEMATICS_SHARED

        # Create shared project with sample data
        result = NG.new(collection=NS_SCHEMATICS, project=SmokeTests.app_name, theme=theme, shared=shared,
                        sample=sample, style=style, prefix=prefix, source_dir=source_dir, webpack=webpack)
        TnsAssert.created(app_name=SmokeTests.app_name, app_data=app_data)
        assert 'Directory is already under version control. Skipping initialization of git.' in result.output, \
            'Git init should be skipped because app is created already existing repo (the one with tests).'

        # Check sample
        if sample:
            # TODO: Implement it
            pass

        # Check theme
        if theme:
            assert App.is_dependency(app_name=SmokeTests.app_name, dependency='nativescript-theme-core')
        else:
            assert not App.is_dependency(app_name=SmokeTests.app_name, dependency='nativescript-theme-core')

        # Check styling
        if style is not None:
            # TODO: Implement it
            pass

        # Check webpack
        if webpack:
            # TODO: Implement it
            pass

        # Update the app
        App.update(app_name=SmokeTests.app_name)

        # Build in release with all the options
        Tns.build(app_name=SmokeTests.app_name, platform=Platform.ANDROID, release=True,
                  bundle=True, aot=True, uglify=True, snapshot=True)
        if Settings.HOST_OS is OSType.OSX:
            Tns.build(app_name=SmokeTests.app_name, platform=Platform.IOS, release=True, for_device=True,
                      bundle=True, aot=True, uglify=True)

        # Run android (only with bundle)
        Tns.run(app_name=SmokeTests.app_name, platform=Platform.ANDROID, bundle=True)
        for text in app_data.texts:
            SmokeTests.emu.wait_for_text(text=text, timeout=30)
            blue_pixels = SmokeTests.emu.get_pixels_by_color(color=Colors.LIGHT_BLUE_ANDROID)
            if theme:
                assert blue_pixels > 1000, 'Default {N} theme is NOT applied.'
            else:
                assert blue_pixels == 0, 'Default {N} theme is applied, but it should not.'

        # Run ios
        if Settings.HOST_OS is OSType.OSX:
            Tns.run(app_name=SmokeTests.app_name, platform=Platform.IOS, bundle=True)
            for text in app_data.texts:
                SmokeTests.sim.wait_for_text(text=text, timeout=30)
                blue_pixels = SmokeTests.emu.get_pixels_by_color(color=Colors.LIGHT_BLUE_IOS)
                if theme:
                    assert blue_pixels > 1000, 'Default {N} theme is NOT applied.'
                else:
                    assert blue_pixels == 0, 'Default {N} theme is applied, but it should not.'
