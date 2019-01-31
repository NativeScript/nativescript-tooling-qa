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

    def test_02_get_run_messages_first_run(self):
        logs = TnsLogs.run_messages(app_name=Settings.AppName.DEFAULT,
                                    platform=Platform.ANDROID,
                                    run_type=RunType.FIRST_TIME)
        # assert 'Skipping node_modules folder!' in logs
        # assert 'Preparing project...' in logs
        # assert 'Project successfully prepared (Android)' in logs
        # assert 'Building project...' in logs
        # assert 'Gradle build...' in logs
        # assert 'Project successfully built.' in logs
        # assert 'Installing on device' in logs
        # assert 'Successfully installed on device' in logs
        assert 'Restarting application on device' in logs
        assert 'Successfully synced application org.nativescript.TestApp on device' in logs
        assert 'ActivityManager: Start proc' in logs
        assert 'activity org.nativescript.TestApp/com.tns.NativeScriptActivity' in logs

    def test_03_get_run_messages_sync_js(self):
        logs = TnsLogs.run_messages(app_name=Settings.AppName.DEFAULT,
                                    platform=Platform.ANDROID,
                                    run_type=RunType.INCREMENTAL,
                                    file_name='main-view-model.js')
        assert 'Preparing project...' in logs
        assert 'Project successfully prepared (Android)' in logs
        assert 'Successfully transferred main-view-model.js on device' in logs
        assert 'Restarting application on device' in logs
        assert 'Successfully synced application org.nativescript.TestApp on device' in logs
        assert 'ActivityManager: Start proc' in logs
        assert 'activity org.nativescript.TestApp/com.tns.NativeScriptActivity' in logs

    def test_04_get_run_messages_sync_js_bundle(self):
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
        assert 'Successfully transferred bundle.js on device' in logs
        assert 'Restarting application on device' in logs
        assert 'Successfully synced application org.nativescript.TestApp on device' in logs
        assert 'ActivityManager: Start proc' in logs
        assert 'activity org.nativescript.TestApp/com.tns.NativeScriptActivity' in logs
        assert 'Refreshing application on device' not in logs
        assert 'hot-update.json on device' not in logs

    def test_05_get_run_messages_sync_js_hmr(self):
        logs = TnsLogs.run_messages(app_name=Settings.AppName.DEFAULT,
                                    platform=Platform.ANDROID,
                                    run_type=RunType.INCREMENTAL,
                                    file_name='main-view-model.js',
                                    hmr=True)
        assert 'File change detected.' in logs
        assert 'main-view-model.js' in logs
        assert 'Webpack compilation complete.' in logs
        assert 'hot-update.json on device' in logs
        assert 'The following modules were updated:' in logs
        assert 'Successfully applied update with hmr hash' in logs
        # TODO: Uncomment when fixed in TnsLogs.run_messages()
        # assert 'Refreshing application on device' in logs
        assert 'Successfully synced application org.nativescript.TestApp on device' in logs
        assert 'Successfully transferred bundle.js on device' not in logs
        # TODO: Uncomment when fixed in TnsLogs.run_messages()
        # assert 'Restarting application on device' not in logs


if __name__ == '__main__':
    unittest.main()
