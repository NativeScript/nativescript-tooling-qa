import unittest

from core.enums.platform_type import Platform
from products.nativescript.tns_logs import TnsLogs


# noinspection PyMethodMayBeStatic
class SyncMessagesTests(unittest.TestCase):

    def test_01_constants(self):
        assert len(TnsLogs.SKIP_NODE_MODULES) == 2

    def test_02_get_prepare_log_strings(self):
        logs = TnsLogs.prepare_messages(platform=Platform.ANDROID, plugins=['tns-core-modules', 'fake-plugin'])
        assert 'Preparing project...' in logs
        assert 'Successfully prepared plugin tns-core-modules for android' in logs
        assert 'Successfully prepared plugin fake-plugin for android' in logs
        assert 'Project successfully prepared (Android)' in logs
        assert len(logs) == 4

    def test_02_refresh_app_messages(self):
        pass


if __name__ == '__main__':
    unittest.main()
