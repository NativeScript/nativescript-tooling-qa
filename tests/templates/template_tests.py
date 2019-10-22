import os

from parameterized import parameterized

from core.base_test.tns_run_test import TnsRunTest
from core.enums.env import EnvironmentType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.simctl import Simctl
from core.utils.file_utils import Folder
from data.const import Colors
from data.templates import Template
from products.nativescript.app import App
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs
from products.nativescript.tns_paths import TnsPaths


# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class TemplateTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    app_folder = TnsPaths.get_app_path(app_name=app_name)

    test_data = [
        [Template.BLANK_JS.name, Template.BLANK_JS],
        [Template.BLANK_TS.name, Template.BLANK_TS],
        [Template.BLANK_NG.name, Template.BLANK_NG],
        [Template.VUE_BLANK.name, Template.VUE_BLANK],
        [Template.DRAWER_NAVIGATION_JS.name, Template.DRAWER_NAVIGATION_JS],
        [Template.DRAWER_NAVIGATION_TS.name, Template.DRAWER_NAVIGATION_TS],
        [Template.DRAWER_NAVIGATION_NG.name, Template.DRAWER_NAVIGATION_NG],
        [Template.DRAWER_NAVIGATION_VUE.name, Template.DRAWER_NAVIGATION_VUE],
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
        [Template.MASTER_DETAIL_VUE.name, Template.MASTER_DETAIL_VUE],
        [Template.PATIENT_CARE_NG.name, Template.PATIENT_CARE_NG],
        [Template.TAB_NAVIGATION_JS.name, Template.TAB_NAVIGATION_JS],
        [Template.TAB_NAVIGATION_TS.name, Template.TAB_NAVIGATION_TS],
        [Template.TAB_NAVIGATION_NG.name, Template.TAB_NAVIGATION_NG]
    ]

    @parameterized.expand(test_data)
    def test(self, template_name, template_info):
        TnsRunTest.setUp(self)

        # Create app
        app_name = template_info.name.replace('template-', '')
        Tns.create(app_name=app_name, template='tns-' + template_name, update=False)
        if Settings.ENV != EnvironmentType.LIVE and Settings.ENV != EnvironmentType.PR:
            App.update(app_name=app_name)

        # Run Android
        result = Tns.run_android(app_name=app_name, device=self.emu.id)
        strings = TnsLogs.run_messages(app_name=app_name, run_type=RunType.UNKNOWN, platform=Platform.ANDROID)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=300)
        if template_info.texts is not None:
            for text in template_info.texts:
                self.emu.wait_for_text(text=text, timeout=60)
        else:
            self.emu.wait_for_main_color(color=Colors.WHITE, timeout=60)

        # Run iOS
        if Settings.HOST_OS is OSType.OSX:
            Simctl.uninstall_all(simulator_info=self.sim)
            result = Tns.run_ios(app_name=app_name, device=self.sim.id)
            strings = TnsLogs.run_messages(app_name=app_name, run_type=RunType.UNKNOWN, platform=Platform.IOS)
            TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=300)
            if template_info.texts is not None:
                for text in template_info.texts:
                    self.sim.wait_for_text(text=text, timeout=60)
            else:
                self.sim.wait_for_main_color(color=Colors.WHITE, timeout=60)

        # Cleanup
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, app_name))
        TnsRunTest.tearDown(self)
