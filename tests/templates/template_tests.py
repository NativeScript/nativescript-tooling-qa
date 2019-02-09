import os

from parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.env import EnvironmentType
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder, File
from core.utils.gradle import Gradle
from core.utils.npm import Npm
from data.const import Colors
from data.templates import Template
from products.nativescript.app import App
from products.nativescript.tns import Tns


# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class TemplateTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_folder = os.path.join(Settings.TEST_RUN_HOME, app_name)
    emu = None
    sim = None

    test_data = [
        [Template.BLANK_JS.name, Template.BLANK_JS],
        [Template.BLANK_TS.name, Template.BLANK_TS],
        [Template.BLANK_NG.name, Template.BLANK_NG],
        [Template.VUE_BLANK.name, Template.VUE_BLANK],
        [Template.DRAWER_NAVIGATION_JS.name, Template.DRAWER_NAVIGATION_JS],
        [Template.DRAWER_NAVIGATION_TS.name, Template.DRAWER_NAVIGATION_TS],
        [Template.DRAWER_NAVIGATION_NG.name, Template.DRAWER_NAVIGATION_NG],
        [Template.HEALTH_SURVEY_NG.name, Template.HEALTH_SURVEY_NG],
        [Template.HELLO_WORLD_JS.name, Template.HELLO_WORLD_JS],
        [Template.HELLO_WORLD_TS.name, Template.HELLO_WORLD_TS],
        [Template.HELLO_WORLD_NG.name, Template.HELLO_WORLD_NG],
        [Template.MASTER_DETAIL_KINVEY_JS.name, Template.MASTER_DETAIL_KINVEY_JS],
        [Template.MASTER_DETAIL_KINVEY_TS.name, Template.MASTER_DETAIL_KINVEY_TS],
        [Template.MASTER_DETAIL_KINVEY_NG.name, Template.MASTER_DETAIL_KINVEY_NG],
        [Template.MASTER_DETAIL_JS.name, Template.MASTER_DETAIL_JS],
        [Template.MASTER_DETAIL_TS.name, Template.MASTER_DETAIL_TS],
        [Template.MASTER_DETAIL_NG.name, Template.MASTER_DETAIL_NG],
        [Template.VUE_MASTER_DETAIL.name, Template.VUE_MASTER_DETAIL],
        [Template.PATIENT_CARE_NG.name, Template.PATIENT_CARE_NG],
        [Template.TAB_NAVIGATION_JS.name, Template.TAB_NAVIGATION_JS],
        [Template.TAB_NAVIGATION_TS.name, Template.TAB_NAVIGATION_TS],
        [Template.TAB_NAVIGATION_NG.name, Template.TAB_NAVIGATION_NG]
    ]

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

    def setUp(self):
        TnsTest.setUp(self)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    @parameterized.expand(test_data)
    def test(self, template_name, template_info):
        # Ensure template local package
        template_folder = os.path.join(Settings.TEST_SUT_HOME, 'templates', 'packages', template_name)
        out_file = os.path.join(Settings.TEST_SUT_HOME, template_name + '.tgz')
        Npm.pack(folder=template_folder, output_file=out_file)
        assert File.exists(out_file), "Failed to pack template: " + template_name

        # Create app
        app_name = template_info.name.replace('template-', '')
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        Tns.create(app_name=app_name, template=template_info.local_package, update=False)
        if Settings.ENV != EnvironmentType.LIVE and Settings.ENV != EnvironmentType.PR:
            App.update(app_name=app_name)

        # Run Android
        Adb.open_home(device_id=self.emu.id)
        Tns.run_android(app_name=app_name, device=self.emu.id, bundle=True, justlaunch=True)
        if template_info.texts is not None:
            for text in template_info.texts:
                self.emu.wait_for_text(text=text, timeout=60)
        else:
            self.emu.wait_for_main_color(color=Colors.WHITE, timeout=60)

        # Run iOS
        if Settings.HOST_OS is OSType.OSX:
            Tns.run_ios(app_name=app_name, device=self.sim.id, bundle=True, justlaunch=True)
            if template_info.texts is not None:
                for text in template_info.texts:
                    self.sim.wait_for_text(text=text, timeout=60)
            else:
                self.sim.wait_for_main_color(color=Colors.WHITE, timeout=60)

        # Cleanup
        Tns.kill()
        Gradle.kill()
        Folder.clean(app_path)
