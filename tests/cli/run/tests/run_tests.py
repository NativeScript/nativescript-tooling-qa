import os
import nose
import time
import unittest
from core.base_test.tns_run_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder, File, Process
from core.utils.device.adb import Adb
from core.utils.device.simctl import Simctl
from core.utils.device.device_manager import DeviceManager
from core.log.log import Log
from data.changes import Changes, Sync
from data.templates import Template
from data.const import Colors
from data.sync.hello_world_js import run_hello_world_js_ts
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs
from products.nativescript.run_type import RunType
from products.nativescript.tns_paths import TnsPaths


class TnsRunJSTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_name_space = Settings.AppName.WITH_SPACE
    app_path = TnsPaths.get_app_path(app_name)
    app_resources_path = TnsPaths.get_path_app_resources(app_name)
    source_project_dir = TnsPaths.get_app_path(app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)
    app_resources_android = os.path.join(app_resources_path, 'Android')
    app_resources_ios = os.path.join(app_resources_path, 'iOS')

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.EMU_API_28)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)
            Simctl.uninstall_all(cls.sim)

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        src = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'logs', 'hello-world-js', 'app.js')
        target = os.path.join(cls.app_path, 'app')
        File.copy(source=src, target=target)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsTest.setUp(self)
        Adb.open_home(self.emu.id)
        Adb.clear_logcat(self.emu.id)
        if Settings.HOST_OS is OSType.OSX:
            Simctl.stop_all(self.sim)

        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        source_src = os.path.join(self.target_project_dir, 'app')
        target_src = os.path.join(self.source_project_dir, 'app')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)

    def test_100_run_android_break_and_fix_app(self):
        """
            Make changes in xml that break the app and then changes thet fix the app.
            Add/remove js files thst break the app and then fix it. Verify recovery.
        """
        # Run app and verify on device
        result = run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu)
    
        # Make changes in xml that will break the app
        Sync.replace(self.app_name, Changes.JSHelloWord.XML_INVALID)
        strings = ['main-page.xml', 'Error: Parsing XML']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text='Exception')
    
        # Revert changes
        Sync.revert(self.app_name, Changes.JSHelloWord.XML_INVALID)
    
        # Verify app is synced and recovered
        strings = ['Successfully synced application']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
        assert not self.emu.is_text_visible(text='Exception')
    
        # Delete app.js and verify app crash with error activity dialog
        app_js_origin_path = os.path.join(self.source_project_dir, 'app', 'app.js')
        app_js_backup_path = os.path.join(self.target_project_dir, 'app', 'app.js')
        File.delete(app_js_origin_path)
    
        # Verify app is synced
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       device=self.emu, run_type=RunType.UNKNOWN)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text='Exception')
    
        # Restore app.js and verify app is synced and recovered
        File.copy(app_js_backup_path, app_js_origin_path)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.UNKNOWN, device=self.emu)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
        assert not self.emu.is_text_visible(text='Exception')
    
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_100_run_ios_break_and_fix_app(self):
        """
            Make changes in xml that break the app and then changes thet fix the app.
            Add/remove js files thst break the app and then fix it. Verify recovery.
        """
        # Run app and verify on device
        result = run_hello_world_js_ts(self.app_name, Platform.IOS, self.sim)
    
        # Make changes in xml that will break the app
        Sync.replace(self.app_name, Changes.JSHelloWord.XML_INVALID)
        strings = ['main-page.xml', 'Error: Parsing XML']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
        # Revert changes
        Sync.revert(self.app_name, Changes.JSHelloWord.XML_INVALID)
    
        # Verify app is synced and recovered
        strings = ['Successfully synced application']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.sim.wait_for_text(text=Changes.JSHelloWord.XML.old_text)
    
    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, 'skip on windows untill we fix wait_rof_log method')
    def test_105_tns_run_android_changes_in_app_resounces(self):
        """
            Make changes in AndroidManifest.xml in App_Resources and verify this triggers rebuild of the app.
            Verify that when run on android changes in AppResources/iOS do not trigger rebuild
        """
        # Run app and verify on device
        result = run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu)
    
        # Make changes in AndroidManifest.xml
        manifest_path = os.path.join(self.app_resources_android, 'src', 'main', 'AndroidManifest.xml')
        File.replace(manifest_path, 'largeScreens="true"', 'largeScreens="false"')
    
        # Verify rebuild is triggered and app is synced
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.FULL, device=self.emu)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
        self.emu.wait_for_text(text=Changes.JSHelloWord.XML.old_text)
    
        # Make changes in AppResources/Android
        File.copy(os.path.join(Settings.TEST_RUN_HOME, 'assets', 'resources', 'android', 'drawable-hdpi', 'icon.png'),
                  os.path.join(self.app_resources_android, 'src', 'main', 'res', 'drawable-hdpi', 'icon.png'))
        # Verify only build for android is triggered
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.FULL, device=self.emu)
        not_existing_strings = ['Xcode build']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
    
        # https://github.com/NativeScript/nativescript-cli/issues/3658
        Tns.kill()
        # Make changes in AppResources/iOS
        File.copy(os.path.join('assets', 'resources', 'ios', 'Default.png'),
                  os.path.join(self.app_resources_ios, 'Assets.xcassets', 'LaunchImage.launchimage', 'Default.png'))
        result = Tns.run_android(app_name=self.app_name, device=self.emu.id)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.UNKNOWN, device=self.emu)
        # Verify no build is triggered
        not_existing_strings = ['Xcode build', 'Gradle build']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
    
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_105_tns_run_ios_changes_in_app_resounces(self):
        """
            Make changes in AndroidManifest.xml in App_Resources and verify this triggers rebuild of the app.
            Verify that when run on android changes in AppResources/iOS do not trigger rebuild
        """
        # Run app and verify on device
        result = run_hello_world_js_ts(self.app_name, Platform.IOS, self.sim)
    
        # Make changes in app resources, add aditional icon
        File.copy(os.path.join(Settings.TEST_RUN_HOME, 'assets', 'resources', 'ios', 'Default.png'),
                  os.path.join(self.app_resources_ios, 'Assets.xcassets', 'icon.png'))
    
        # Verify rebuild is triggered and app is synced
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.IOS,
                                       run_type=RunType.FULL, device=self.sim)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
        self.sim.wait_for_text(text=Changes.JSHelloWord.XML.old_text)
    
        # Make changes in AppResources/IOS
        File.copy(os.path.join(os.path.join(Settings.TEST_RUN_HOME, 'assets', 'resources', 'ios', 'Default.png')),
                  os.path.join(self.app_resources_ios, 'Assets.xcassets', 'AppIcon.appiconset', 'icon-20.png'))
        # Verify only build for ios is triggered
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.IOS,
                                       run_type=RunType.FULL, device=self.sim)
        not_existing_strings = ['Gradle build']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
    
        # https://github.com/NativeScript/nativescript-cli/issues/3658
        Tns.kill()
        # Make changes in AppResources/Android
        File.copy(os.path.join(Settings.TEST_RUN_HOME, 'assets', 'resources', 'android', 'drawable-hdpi', 'icon.png'),
                  os.path.join(self.app_resources_android, 'src', 'main', 'res', 'drawable-hdpi', 'icon.png'))
        result = Tns.run_ios(app_name=self.app_name, device=self.sim.id)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.IOS,
                                       run_type=RunType.UNKNOWN, device=self.sim)
        # Verify no build is triggered
        not_existing_strings = ['Xcode build', 'Gradle build']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
    
    def test_110_tns_run_android_release(self):
        # Run app and verify on device
        result = Tns.run_android(app_name=self.app_name, release=True, verify=True, emulator=True)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.FIRST_TIME, device=self.emu)
        strings.remove('Restarting application on device')
        strings.remove('Successfully synced application org.nativescript.TestApp on device')
        # Verify https://github.com/NativeScript/android-runtime/issues/1024
        not_existing_strings = ['JS:']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
        self.emu.wait_for_text(text=Changes.JSHelloWord.XML.old_text)
        blue_count = self.emu.get_pixels_by_color(color=Colors.LIGHT_BLUE)
        assert blue_count > 100, 'Failed to find blue color on {0}'.format(self.emu.name)
    
        Tns.kill()
        # Make changes in js, css and xml files
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.XML)
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.CSS)
    
        # Run with --release again and verify changes are deployed on device
        result = Tns.run_android(app_name=self.app_name, release=True, verify=True, emulator=True)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.new_text)
        self.emu.wait_for_text(text=Changes.JSHelloWord.XML.new_text)
        self.emu.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count * 2, delta=25)
    
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_110_tns_run_ios_release(self):
        # Run app and verify on device
        result = Tns.run_ios(app_name=self.app_name, release=True, verify=True, emulator=True)
        strings = ['Webpack compilation complete', 'Project successfully built', 'Successfully started on device']
        # Verify console logs are not displayed in release builds
        not_existing_strings = ['JS:']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
        self.sim.wait_for_text(text=Changes.JSHelloWord.XML.old_text)
        blue_count = self.sim.get_pixels_by_color(color=Colors.LIGHT_BLUE)
        assert blue_count > 100, 'Failed to find blue color on {0}'.format(self.sim.name)
    
        Tns.kill()
        # Make changes in js, css and xml files
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.XML)
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.CSS)
    
        # Run with --release again and verify changes are deployed on device
        result = Tns.run_ios(app_name=self.app_name, release=True, verify=True, emulator=True)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.new_text)
        self.sim.wait_for_text(text=Changes.JSHelloWord.XML.new_text)
        self.sim.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count * 2, delta=25)
    
    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, 'skip on windows untill we fix wait_rof_log method')
    def test_115_tns_run_android_add_remove_files_and_folders(self):
        """
        Add/delete files and folders should be synced properly
        """
        # Run app and verify on device
        result = run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu)
    
        # Add new file
        # To verify that file is synced on device we have to refer some function
        # from it and verify it is executed. We will use console.log
        app_folder = os.path.join(self.source_project_dir, 'app')
        new_file = os.path.join(app_folder, 'test.js')
        renamed_file = os.path.join(app_folder, 'test_2.js')
        app_js_file = os.path.join(app_folder, 'app.js')
        File.write(new_file, "console.log('test.js synced!!!');")
        File.append(app_js_file, "require('./test.js');")
        strings = ["JS: test.js synced!!!"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
        # Rename file
        os.rename(new_file, renamed_file)
        File.replace(renamed_file, 'test.js', 'renamed file')
        File.replace(app_js_file, 'test.js', 'test_2.js')
        strings = ["JS: renamed file synced!!!"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
        # Delete file
        File.delete(renamed_file)
        strings = ["Module build failed: Error: ENOENT", 'Successfully synced application']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text='Exception')
    
        File.replace(app_js_file, "require('./test_2.js');", ' ')
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       device=self.emu, run_type=RunType.UNKNOWN)
        not_existing_strings = ['12345']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
    
        # Add folder
        folder_name = os.path.join(app_folder, 'test_folder')
        new_file = os.path.join(folder_name, 'test_in_folder.js')
        Folder.create(folder_name)
        File.write(new_file, "console.log('test_in_folder.js synced!!!');")
        File.append(app_js_file, "require('./test_folder/test_in_folder.js');")
        strings = ["JS: test_in_folder.js synced!!!"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
        # Delete folder
        Folder.clean(folder_name)
        strings = ["Module build failed: Error: ENOENT"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text='Exception')
    
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_115_tns_run_ios_add_remove_files_and_folders(self):
        """
        Add/delete files and folders should be synced properly
        """
        # Run app and verify on device
        result = run_hello_world_js_ts(self.app_name, Platform.IOS, self.sim)
    
        # Add new file
        # To verify that file is synced on device we have to refer some function
        # from it and verify it is executed. We will use console.log
        app_folder = os.path.join(self.source_project_dir, 'app')
        new_file = os.path.join(app_folder, 'test.js')
        renamed_file = os.path.join(app_folder, 'test_2.js')
        app_js_file = os.path.join(app_folder, 'main-view-model.js')
        File.write(new_file, "console.log('test.js synced!!!');")
        File.append(app_js_file, "require('./test.js');")
        strings = ["test.js synced!!!"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
        # Rename file
        os.rename(new_file, renamed_file)
        File.replace(renamed_file, 'test.js', 'renamed file')
        File.replace(app_js_file, 'test.js', 'test_2.js')
        strings = ["renamed file synced!!!"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
        # Delete file
        File.delete(renamed_file)
        strings = ["Module build failed: Error: ENOENT", "NativeScript debugger detached"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
        File.replace(app_js_file, "require('./test_2.js');", ' ')
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.IOS,
                                       device=self.sim, run_type=RunType.UNKNOWN)
        not_existing_strings = ['123']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
    
        # Add folder
        folder_name = os.path.join(app_folder, 'test_folder')
        new_file = os.path.join(folder_name, 'test_in_folder.js')
        Folder.create(folder_name)
        File.write(new_file, "console.log('test_in_folder.js synced!!!');")
        File.append(app_js_file, "require('./test_folder/test_in_folder.js');")
        strings = ["test_in_folder.js synced!!!"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
    
        # Delete folder
        Folder.clean(folder_name)
        strings = ["Module build failed: Error: ENOENT"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
    def test_120_tns_run_android_just_launch(self):
        """
        This test verify following things:
        1. `--justlaunch` option release the console.
        2. Full rebuild and prepare are not trigerred if no changes are done.
        3. Incremental prepare is triggered if js, xml and css files are changed.
        """
        # Run app with --justlaunch and verify on device
        result = run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu, just_launch=True)
        # On some machines it takes time for thr process to die
        time.sleep(5)
        assert not Process.is_running_by_name('node')
    
        # Execute run with --justlaunch again and verify no rebuild is triggered
        result = Tns.run_android(app_name=self.app_name, emulator=True, just_launch=True)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.INCREMENTAL, device=self.emu, just_launch=True)
        strings.remove('Refreshing application on device')
        not_existing_strings = ['Preparing project...', 'Webpack compilation complete.']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
    
        # Make changes in js, css and xml files
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.XML)
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.CSS)
    
        # Execute run with --justlaunch again and verify prepare is triggered
        result = Tns.run_android(app_name=self.app_name, emulator=True, just_launch=True)
        strings = ['Project successfully prepared', 'Webpack compilation complete']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.XML.new_text)
    
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_120_tns_run_ios_just_launch(self):
        """
        This test verify following things:
        1. `--justlaunch` option release the console.
        2. Full rebuild and prepare are not trigerred if no changes are done.
        3. Incremental prepare is triggered if js, xml and css files are changed.
        """
        # Run app with --justlaunch and verify on device
        result = run_hello_world_js_ts(self.app_name, Platform.IOS, self.sim, just_launch=True)
        # On some machines it takes time for thr process to die
        time.sleep(7)
        assert not Process.is_running_by_name('node')
    
        # Execute run with --justlaunch again and verify no rebuild is triggered
        result = Tns.run_ios(app_name=self.app_name, emulator=True, just_launch=True)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.IOS,
                                       run_type=RunType.INCREMENTAL, device=self.sim, just_launch=True)
        strings.remove('Refreshing application on device')
        not_existing_strings = ['Preparing project...', 'Webpack compilation complete.']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
    
        # Make changes in js, css and xml files
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.XML)
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.CSS)
    
        # Execute run with --justlaunch again and verify prepare is triggered
        result = Tns.run_ios(app_name=self.app_name, emulator=True, just_launch=True)
        strings = ['Project successfully prepared', 'Webpack compilation complete']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.sim.wait_for_text(text=Changes.JSHelloWord.XML.new_text)
    
    @unittest.skip("Skip because of https://github.com/NativeScript/nativescript-cli/issues/4607")
    def test_290_tns_run_android_should_refresh_images(self):
        """
        Test for https://github.com/NativeScript/nativescript-cli/issues/2981
        """
        # Update app to reference picture from app folder
        source_file = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'issues', 'nativescript-cli-2981', 'main-page.xml')
        dest_file = os.path.join(self.app_path, 'app', 'main-page.xml')
        File.copy(source_file, dest_file)
    
        # Copy image file to app folder
        source_file = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'resources', 'star.png')
        dest_file = os.path.join(self.app_path, 'app', 'test.png')
        File.copy(source_file, dest_file)
        result = Tns.run_android(app_name=self.app_name, verify=True, device=self.emu.id)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.FIRST_TIME, device=self.emu)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        yellow_count = self.emu.get_pixels_by_color(color=Colors.YELLOW_ICON)
        green_count = self.emu.get_pixels_by_color(color=Colors.GREEN_ICON)
    
        # Verify the referenced image file is displayed on device screen
        assert yellow_count > 0, 'Failed to find yellow color on {0}'.format(self.emu.name)
        assert green_count == 0, 'Found green color on {0}'.format(self.emu.name)
    
        # Change the image file
        source_file = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'resources', 'android',
                                   'drawable-hdpi', 'background.png')
        dest_file = os.path.join(self.app_path, 'app', 'test.png')
        File.copy(source_file, dest_file)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.UNKNOWN, device=self.emu)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
        # Verify the new image is synced and displayed on device screen
        yellow_count = self.emu.get_pixels_by_color(color=Colors.YELLOW_ICON)
        green_count = self.emu.get_pixels_by_color(color=Colors.GREEN_ICON)
        assert green_count > 0, 'Failed to find green color on {0}'.format(self.emu.name)
        assert yellow_count == 0, 'Found yellow color on {0}'.format(self.emu.name)
    
    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, 'skip on windows untill we fix wait_rof_log method')
    def test_300_tns_run_android_clean(self):
        """
        If  set --clean rebuilds the native project
        """
        # Run the project once so it is build for the first time
        result = run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu, just_launch=True)
    
        # Verify run --clean without changes skip prepare and rebuild of native project
        result = Tns.run_android(app_name=self.app_name, verify=True, device=self.emu.id, clean=True, just_launch=True)
        strings = ['Skipping prepare', 'Building project', 'Gradle clean']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.XML.old_text)
    
        # Verify if changes are applied and then run with clean it will apply changes on device
        # Verify https://github.com/NativeScript/nativescript-cli/issues/2670 run --clean does
        # clean build only the first time
        Sync.replace(self.app_name, Changes.JSHelloWord.XML)
        result = Tns.run_android(app_name=self.app_name, verify=True, device=self.emu.id, clean=True)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.FULL, device=self.emu)
        strings.append('Gradle clean')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.XML.new_text)
    
        # Make changes again and verify changes are synced and clean build is not triggered again
        Sync.revert(self.app_name, Changes.JSHelloWord.XML)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.INCREMENTAL, device=self.emu, file_name='main-page.xml')
        not_existing_strings = ['Gradle clean']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
    
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_300_tns_run_ios_clean(self):
        """
        If  set --clean rebuilds the native project
        """
        # Run the project once so it is build for the first time
        result = run_hello_world_js_ts(self.app_name, Platform.IOS, self.sim, just_launch=True)
    
        # Verify run --clean without changes rebuilds native project
        result = Tns.run_ios(app_name=self.app_name, verify=True, device=self.sim.id, clean=True, just_launch=True)
        strings = ['Building project', 'Xcode build...']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.sim.wait_for_text(text=Changes.JSHelloWord.XML.old_text)
    
        # Verify if changes are applied and then run with clean it will apply changes on device
        # Verify https://github.com/NativeScript/nativescript-cli/issues/2670 run --clean does
        # clean build only the first time
        Sync.replace(self.app_name, Changes.JSHelloWord.XML)
        result = Tns.run_ios(app_name=self.app_name, verify=True, device=self.sim.id, clean=True)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.IOS,
                                       run_type=RunType.FULL, device=self.sim)
        strings.append('Xcode build...')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.sim.wait_for_text(text=Changes.JSHelloWord.XML.new_text)
    
        # Make changes again and verify changes are synced and clean build is not triggered again
        Sync.revert(self.app_name, Changes.JSHelloWord.XML)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.IOS,
                                       run_type=RunType.INCREMENTAL, device=self.sim, file_name='main-page.xml')
        not_existing_strings = ['Xcode build...']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_strings)
    
    @unittest.skip("Skip because of https://github.com/NativeScript/nativescript-dev-webpack/issues/899")
    def test_310_tns_run_android_sync_changes_in_node_modules(self):
        """
        Verify changes in node_modules are synced during run command
        """
        # Run the project
        result = run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu, sync_all_files=True)
    
        # Make code changes in tns-core-modules verify livesync is triggered
        Sync.replace(self.app_name, Changes.NodeModules.TNS_MODULES)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.INCREMENTAL, device=self.emu, file_name='application-common.js')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
    
    @unittest.skip("Skip because of https://github.com/NativeScript/nativescript-dev-webpack/issues/899")
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_310_tns_run_ios_sync_changes_in_node_modules(self):
        """
        Verify changes in node_modules are synced during run command
        """
        # Run the project
        result = run_hello_world_js_ts(self.app_name, Platform.IOS, self.sim, sync_all_files=True)
    
        # Make code changes in tns-core-modules verify livesync is triggered
        Sync.replace(self.app_name, Changes.NodeModules.TNS_MODULES)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.INCREMENTAL, device=self.emu, file_name='application-common.js')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
    
    def test_315_tns_run_android_sync_changes_in_aar_files(self):
        """
        Livesync should sync aar file changes inside a plugin
        https://github.com/NativeScript/nativescript-cli/issues/3610
        """
        # Add plugin and run the project
        Tns.plugin_add('nativescript-camera', self.app_name)
        result = run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu, sync_all_files=True)
    
        # Make  changes in nativescript-camera .aar file and  verify livesync is triggered
        new_aar = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'issues', 'nativescript-cli-3932',
                               'nativescript-ui-listview', 'platforms', 'android', 'TNSListView-release.aar')
        target_aar = os.path.join(self.app_name, 'node_modules', 'nativescript-camera', 'platforms', 'android')
        File.copy(new_aar, target_aar)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID,
                                       run_type=RunType.FULL, device=self.emu)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
    
    def test_320_tns_run_android_should_warn_if_package_ids_dont_match(self):
        """
        If bundle identifiers in package.json and app.gradle do not match CLI should warn the user.
        """
    
        # Change app id in app.gradle file
        app_gradle = os.path.join(Settings.TEST_RUN_HOME, self.app_name, 'app', 'App_Resources',
                                  'Android', 'app.gradle')
        File.replace(app_gradle, old_string='generatedDensities = []',
                     new_string='applicationId = "org.nativescript.MyApp"')
    
        # Run the app on device and verify the warnings
        result = Tns.run_android(app_name=self.app_name, just_launch=False)
        strings = ["WARNING: The Application identifier is different from the one inside \"package.json\" file.",
                   "NativeScript CLI might not work properly.",
                   "Project successfully built"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_320_tns_run_ios_should_warn_if_package_ids_dont_match(self):
        """
        If bundle identifiers in package.json and Info.plist do not match CLI should warn the user.
        """
    
        # Change app id in app.gradle file
        old_string = "<string>${EXECUTABLE_NAME}</string>"
        new_string = "<string>${EXECUTABLE_NAME}</string>" \
                     "<key>CFBundleIdentifier</key>" \
                     "<string>org.nativescript.myapp</string>"
        info_plist = os.path.join(Settings.TEST_RUN_HOME, self.app_resources_ios, 'Info.plist')
    
        File.replace(info_plist, old_string, new_string)
    
        # Run the app on device and verify the warnings
        result = Tns.run_ios(app_name=self.app_name, just_launch=False)
        strings = ["[WARNING]: The CFBundleIdentifier key inside the 'Info.plist' will be overriden",
                   "Project successfully built"]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
    def test_325_tns_run_android_should_start_emulator(self):
        """
        `tns run android` should start emulator if device is not connected.
        """
        # Run the test only if there are no connected devices
        conected_devices = Adb.get_ids()
        if conected_devices.__len__() == 0:
            DeviceManager.Emulator.stop()
            result = Tns.run_android(self.app_name)
            strings = ['Starting Android emulator with image']
            TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=120)
            DeviceManager.Emulator.stop()
            DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        else:
            raise nose.SkipTest('This test is not valid when devices are connected.')
    
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_325_tns_run_ios_should_start_simulator(self):
        """
        `tns run android` should start emulator if device is not connected.
        """
        # Run the test only if there are no connected devices
        conected_devices = DeviceManager.get_devices(device_type=Platform.IOS)
        if conected_devices.__len__() == 0:
            DeviceManager.Simulator.stop()
            result = Tns.run_ios(self.app_name)
            strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.IOS,
                                           run_type=RunType.FULL, device=self.sim)
            TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=120)
            DeviceManager.Simulator.stop()
            DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)
        else:
            raise nose.SkipTest('This test is not valid when devices are connected.')
    
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_345_tns_run_ios_source_code_in_ios_part_plugin(self):
        """
        https://github.com/NativeScript/nativescript-cli/issues/3650
        """
        # Add plugin with source code in iOS part of the plugin
        plugin_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'plugins', 'sample-plugin', 'src')
        Tns.plugin_add(plugin_path, path=self.app_name, verify=True)
    
        # Replace main-page.js to call method from the source code of the plugin
        source_js = os.path.join(Settings.TEST_RUN_HOME, 'assets', "issues", 'nativescript-cli-3650',
                                 'main-view-model.js')
        target_js = os.path.join(Settings.TEST_RUN_HOME, self.app_name, 'app', 'main-view-model.js')
        File.copy(source_js, target_js)
    
        result = Tns.run_ios(self.app_name, emulator=True)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.IOS,
                                       run_type=RunType.FIRST_TIME, device=self.sim)
        strings.append('Hey!')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
        # Verify app looks correct inside simulator
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
    
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_350_tns_run_ios_source_code_in_app_resources(self):
        """
        https://github.com/NativeScript/nativescript-cli/issues/4343
        """
        # Add plugin with source code in iOS part of the plugin
        source_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'issues', 'nativescript-cli-4343', 'src')
        dest_path = os.path.join(self.app_resources_ios, 'src')
        Folder.copy(source_path, dest_path, clean_target=False)
    
        # Replace main-view-model.js to call method from the source code in app resources
        source_js = os.path.join(Settings.TEST_RUN_HOME, 'assets', "issues", 'nativescript-cli-3650',
                                 'main-view-model.js')
        target_js = os.path.join(Settings.TEST_RUN_HOME, self.app_name, 'app', 'main-view-model.js')
        File.copy(source_js, target_js)
    
        result = Tns.run_ios(self.app_name, emulator=True)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.IOS,
                                       run_type=RunType.FIRST_TIME, device=self.sim)
        strings.append('Hey Native!')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    
        # Verify app looks correct inside simulator
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.old_text)

    def test_355_tns_run_android_delete_node_modules(self):
        """
        Run should not fail if node_modules folder is deleted
        https://github.com/NativeScript/nativescript-cli/issues/3944
        """
        # Run the project with --justLaunch
        run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu, just_launch=True)
    
        # Delete node_modules
        node_modules = os.path.join(Settings.TEST_RUN_HOME, self.app_name, 'node_modules')
        Folder.clean(node_modules)
    
        # Run the project again, verify it is build and node_modules folder exists
        run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu, just_launch=True)
        assert Folder.exists(node_modules)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_360_tns_run_ios_on_folder_with_spaces(self):
        """
        `tns run ios` for apps with spaces
        """
        Tns.create(app_name=self.app_name_space, template=Template.HELLO_WORLD_JS.local_package, update=False)
        app_name = '"' + self.app_name_space + '"'
        run_hello_world_js_ts(app_name, Platform.ANDROID, self.emu, just_launch=True)

    @unittest.skipIf(Settings.HOST_OS == OSType.LINUX, '`shell cp -r` fails for some reason on emulators on Linux.')
    def test_365_tns_run_android_should_respect_adb_errors(self):
        """
        If device memory is full and error is thrown during deploy cli should respect it
        https://github.com/NativeScript/nativescript-cli/issues/2170
        """
        # Deploy the app to make sure we have something at /data/data/org.nativescript.TestApp
        result = run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu, just_launch=True)
    
        # Use all the disk space on emulator
        for index in range(1, 3000):
            command = "shell cp -r /data/data/org.nativescript.TestApp /data/data/org.nativescript.TestApp" + str(index)
            result = Adb.run_adb_command(device_id=self.emu.id, command=command)
            Log.info(result.output)
            if "No space left on device" in result.output:
                break
    
        # Create new app
        Tns.create(app_name='TestApp2', template=Template.HELLO_WORLD_JS.local_package, update=False)
    
        # Run the app and verify there is appropriate error
        result = Tns.run_android('TestApp2', verify=True, device=self.emu.id, just_launch=True)
        strings = ['No space left on device']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
