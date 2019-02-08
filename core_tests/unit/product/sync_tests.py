import unittest

from core.enums.platform_type import Platform
from core.settings import Settings
from products.nativescript.run_type import RunType
from products.nativescript.tns_logs import TnsLogs


# noinspection PyMethodMayBeStatic
class SyncMessagesTests(unittest.TestCase):

    def test_01_constants(self):
        assert len(TnsLogs.SKIP_NODE_MODULES) == 2

    def test_02_get_prepare_messages(self):
        logs = TnsLogs.prepare_messages(platform=Platform.ANDROID, plugins=['tns-core-modules', 'fake-plugin'])
        assert 'Preparing project...' in logs
        assert 'Successfully prepared plugin tns-core-modules for android' in logs
        assert 'Successfully prepared plugin fake-plugin for android' in logs
        assert 'Project successfully prepared (Android)' in logs
        assert len(logs) == 4

    def test_10_get_run_messages_first_run(self):
        logs = TnsLogs.run_messages(app_name='QAApp',
                                    platform=Platform.ANDROID,
                                    run_type=RunType.FIRST_TIME,
                                    file_name=None)
        assert 'Skipping prepare.' not in logs
        assert 'Preparing project...' in logs
        assert 'Project successfully prepared (Android)' in logs
        assert 'Building project...' in logs
        assert 'Gradle build...' in logs
        assert 'Xcode build...' not in logs
        assert 'Project successfully built.' in logs
        assert 'Installing on device' in logs
        assert 'Successfully installed' in logs
        assert 'Restarting application on device' in logs
        assert 'Refreshing application on device' not in logs
        assert 'Successfully synced application org.nativescript.QAApp on device' in logs
        assert 'ActivityManager: Start proc' in logs
        assert 'activity org.nativescript.QAApp/com.tns.NativeScriptActivity' in logs

    def test_11_get_run_messages_sync_js(self):
        logs = TnsLogs.run_messages(app_name=Settings.AppName.DEFAULT,
                                    platform=Platform.ANDROID,
                                    run_type=RunType.INCREMENTAL,
                                    file_name='main-view-model.js')
        assert 'Preparing project...' in logs
        assert 'Project successfully prepared (Android)' in logs
        assert 'Successfully transferred main-view-model.js' in logs
        assert 'Restarting application on device' in logs
        assert 'Successfully synced application org.nativescript.TestApp on device' in logs
        assert 'ActivityManager: Start proc' in logs
        assert 'activity org.nativescript.TestApp/com.tns.NativeScriptActivity' in logs

    def test_12_get_run_messages_sync_js_bundle(self):
        logs = TnsLogs.run_messages(app_name=Settings.AppName.DEFAULT,
                                    platform=Platform.ANDROID,
                                    run_type=RunType.INCREMENTAL,
                                    file_name='main-view-model.js',
                                    bundle=True)
        assert 'File change detected.' in logs
        assert 'main-view-model.js' in logs
        assert 'Webpack compilation complete.' in logs
        assert 'Preparing project...' in logs
        assert 'Project successfully prepared (Android)' in logs
        assert 'Successfully transferred bundle.js' in logs
        assert 'Successfully transferred vendor.js' not in logs
        assert 'Restarting application on device' in logs
        assert 'Successfully synced application org.nativescript.TestApp on device' in logs
        assert 'ActivityManager: Start proc' in logs
        assert 'activity org.nativescript.TestApp/com.tns.NativeScriptActivity' in logs
        assert 'Refreshing application on device' not in logs
        assert 'hot-update.json on device' not in logs

    def test_12_get_run_messages_sync_js_bundle_uglify(self):
        logs = TnsLogs.run_messages(app_name=Settings.AppName.DEFAULT,
                                    platform=Platform.ANDROID,
                                    run_type=RunType.INCREMENTAL,
                                    file_name='main-view-model.js',
                                    bundle=True, uglify=True)
        assert 'Skipping prepare.' not in logs
        assert 'File change detected.' in logs
        assert 'main-view-model.js' in logs
        assert 'Webpack compilation complete.' in logs
        assert 'Preparing project...' in logs
        assert 'Project successfully prepared (Android)' in logs
        assert 'Successfully transferred bundle.js' in logs
        assert 'Successfully transferred vendor.js' in logs
        assert 'Restarting application on device' in logs
        assert 'Successfully synced application org.nativescript.TestApp on device' in logs
        assert 'ActivityManager: Start proc' in logs
        assert 'activity org.nativescript.TestApp/com.tns.NativeScriptActivity' in logs
        assert 'Refreshing application on device' not in logs
        assert 'hot-update.json on device' not in logs

    def test_13_get_run_messages_sync_js_hmr(self):
        logs = TnsLogs.run_messages(app_name=Settings.AppName.DEFAULT,
                                    platform=Platform.ANDROID,
                                    run_type=RunType.INCREMENTAL,
                                    file_name='main-view-model.js',
                                    hmr=True)
        assert 'File change detected.' in logs
        assert 'main-view-model.js' in logs
        assert 'Webpack compilation complete.' in logs
        assert 'hot-update.json' in logs
        assert 'HMR: The following modules were updated:' in logs
        assert 'HMR: Successfully applied update with hmr hash' in logs
        assert 'Refreshing application on device' in logs
        assert 'Successfully synced application org.nativescript.TestApp on device' in logs
        assert 'Successfully transferred bundle.js on device' not in logs
        assert 'Restarting application on device' not in logs

    def test_14_get_run_messages_sync_xml_bundle_no_hmr(self):
        logs = TnsLogs.run_messages(app_name=Settings.AppName.DEFAULT, platform=Platform.ANDROID,
                                    run_type=RunType.INCREMENTAL, bundle=True, hmr=False, file_name='main-page.xml',
                                    instrumented=True)
        assert 'Refreshing application on device' not in logs
        assert 'Restarting application on device' in logs

    def test_15_get_run_messages_sync_xml_bundle_and_uglify(self):
        logs = TnsLogs.run_messages(app_name=Settings.AppName.DEFAULT, platform=Platform.ANDROID,
                                    run_type=RunType.INCREMENTAL, bundle=True, hmr=False, uglify=True,
                                    file_name='main-page.xml',
                                    instrumented=True)
        assert 'Refreshing application on device' not in logs
        assert 'Restarting application on device' in logs


if __name__ == '__main__':
    unittest.main()
