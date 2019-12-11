# pylint: disable=redefined-builtin
"""
Tests for tns run on project without tns-core-modules package.
See https://github.com/NativeScript/nativescript-dev-webpack/issues/1089
"""
import os

from parameterized import parameterized

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.simctl import Simctl
from core.utils.file_utils import Folder, File
from core.utils.npm import Npm
from data.templates import Template
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class TestRunWithScopedPackages(TnsRunTest):
    test_data = [
        [Template.HELLO_WORLD_JS.name.replace('template-', ''), Template.HELLO_WORLD_JS],
        [Template.HELLO_WORLD_TS.name.replace('template-', ''), Template.HELLO_WORLD_TS],
        [Template.HELLO_WORLD_NG.name.replace('template-', ''), Template.HELLO_WORLD_NG],
        [Template.MASTER_DETAIL_NG.name.replace('template-', ''), Template.MASTER_DETAIL_NG],
    ]

    @parameterized.expand(test_data)
    def test_scoped_package_only(self, app_name, template_info):
        TnsRunTest.setUp(self)

        # Create app
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        Tns.create(app_name=app_name, template=template_info.local_package, update=True)
        Npm.uninstall(package='tns-core-modules', option='--save', folder=app_path)
        Npm.install(package=Settings.Packages.NATIVESCRIPT_CORE, option='--save --save-exact', folder=app_path)

        # Replace imports
        if template_info == Template.HELLO_WORLD_TS:
            files = File.find_by_extension(folder=os.path.join(app_path, 'app'), extension='ts')
            for file in files:
                File.replace(path=file, old_string='tns-core-modules', new_string='@nativescript/core', fail_safe=True)
        if template_info == Template.MASTER_DETAIL_NG:
            files = File.find_by_extension(folder=os.path.join(app_path, 'src'), extension='ts')
            for file in files:
                File.replace(path=file, old_string='tns-core-modules', new_string='@nativescript/core', fail_safe=True)

        Tns.platform_add_android(app_name=app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Run Android
        result = Tns.run_android(app_name=app_name, device=self.emu.id)
        strings = TnsLogs.run_messages(app_name=app_name, run_type=RunType.UNKNOWN, platform=Platform.ANDROID)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=300)
        for text in template_info.texts:
            self.emu.wait_for_text(text=text, timeout=60)

        # Run iOS
        Tns.kill()
        if Settings.HOST_OS is OSType.OSX:
            Simctl.uninstall_all(simulator_info=self.sim)
            result = Tns.run_ios(app_name=app_name, device=self.sim.id)
            strings = TnsLogs.run_messages(app_name=app_name, run_type=RunType.UNKNOWN, platform=Platform.IOS)
            TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=300)
            for text in template_info.texts:
                self.sim.wait_for_text(text=text, timeout=60)

        # Cleanup
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, app_name))
        TnsRunTest.tearDown(self)
