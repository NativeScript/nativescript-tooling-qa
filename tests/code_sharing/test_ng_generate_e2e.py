"""
Tests for `ng g` while livesync is running in same time.
"""
import os
import unittest
from time import sleep

from core.base_test.tns_run_test import TnsRunTest
from core.enums.app_type import AppType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder, File
from products.angular.ng import NG, NS_SCHEMATICS
from products.nativescript.tns import Tns
from products.nativescript.tns_assert import TnsAssert
from products.nativescript.tns_logs import TnsLogs
from products.nativescript.tns_paths import TnsPaths


class NGGenE2ETestsNS(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    app_path = TnsPaths.get_app_path(app_name=app_name)

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        NG.kill()

    def setUp(self):
        TnsRunTest.setUp(self)
        NG.kill()

    def tearDown(self):
        NG.kill()
        TnsRunTest.tearDown(self)

    def test_100_ns_generate_during_run_android(self):
        NGGenE2ETestsNS.workflow(app_name=self.app_name, device=self.emu, platform=Platform.ANDROID, shared=False)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Skip iOS tests on non macOS machines.')
    def test_100_ns_generate_during_run_ios(self):
        NGGenE2ETestsNS.workflow(app_name=self.app_name, device=self.sim, platform=Platform.IOS, shared=False)

    def test_200_shared_generate_during_run_android(self):
        NGGenE2ETestsNS.workflow(app_name=self.app_name, device=self.emu, platform=Platform.ANDROID, shared=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Skip iOS tests on non macOS machines.')
    def test_200_shared_generate_during_run_ios(self):
        NGGenE2ETestsNS.workflow(app_name=self.app_name, device=self.sim, platform=Platform.IOS, shared=True)

    @staticmethod
    def workflow(app_name, device, platform, shared):
        # Create an app
        app_path = TnsPaths.get_app_path(app_name=app_name)
        Folder.clean(app_path)
        NG.new(collection=NS_SCHEMATICS, project=app_name, shared=shared)
        TnsAssert.created(app_name=app_name, app_data=None)

        # Run app initially
        text = 'TAP'
        if shared:
            text = 'Welcome to'

        result = Tns.run(app_name=app_name, platform=platform, emulator=True, hmr=True)
        strings = TnsLogs.run_messages(app_name=app_name, platform=platform, hmr=True, app_type=AppType.NG)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=300)
        device.wait_for_text(text=text)

        # Generate module and component
        NG.exec_command(command='g m module-test', cwd=app_path)
        sleep(3)
        NG.exec_command(command='g c module-test/component-test', cwd=app_path)
        sleep(3)

        # Update app.modules.ts
        app_module_name = 'app.module.ts'
        app_module_path = os.path.join(app_path, 'app', app_module_name)
        old_string = "import { HomeComponent } from './home/home.component';"
        new_string = "import { ComponentTestComponent } from './module-test/component-test/component-test.component';"
        if shared:
            app_module_name = 'app.module.tns.ts'
            app_module_path = os.path.join(app_path, 'src', 'app', app_module_name)
            old_string = "import { HomeComponent } from '@src/app/home/home.component';"
            new_string = \
                "import { ComponentTestComponent } from '@src/app/module-test/component-test/component-test.component';"
        File.replace(path=app_module_path, old_string=old_string, new_string=new_string)
        File.replace(path=app_module_path, old_string='HomeComponent,', new_string='ComponentTestComponent,')
        sleep(3)

        # Update app-routing.module.ts
        app_routing_module_name = 'app-routing.module.ts'
        app_routing_module_path = os.path.join(app_path, 'app', app_routing_module_name)
        old_string = "import { HomeComponent } from './home/home.component';"
        new_string = "import { ComponentTestComponent } from './module-test/component-test/component-test.component';"
        if shared:
            app_routing_module_name = 'app.routes.ts'
            app_routing_module_path = os.path.join(app_path, 'src', 'app', app_routing_module_name)
            old_string = "import { HomeComponent } from '@src/app/home/home.component';"
            new_string = \
                "import { ComponentTestComponent } from '@src/app/module-test/component-test/component-test.component';"
        File.replace(path=app_routing_module_path, old_string=old_string, new_string=new_string)
        File.replace(path=app_routing_module_path, old_string='HomeComponent', new_string='ComponentTestComponent')
        sleep(3)

        # Verify app is updated
        logs = [app_module_name.replace('.tns', ''),
                app_routing_module_name.replace('.tns', ''),
                'Successfully synced application']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=logs, timeout=120)
        device.wait_for_text(text='component-test works!')
