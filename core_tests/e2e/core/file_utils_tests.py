import os

from core.base_test.tns_test import TnsTest
from core.settings.Settings import TEST_RUN_HOME
from core.utils.file_utils import File, Folder


# noinspection PyMethodMayBeStatic
class AdbTests(TnsTest):

    def test_01_file_dowload(self):
        file_name = "test.apk"
        file_path_default = TEST_RUN_HOME
        file_path = os.path.join(TEST_RUN_HOME, "test")
        url = "https://github.com/webdriverio/native-demo-app/releases/download/0.2.1/Android-NativeDemoApp-0.2.1.apk"
        File.download_file(file_name, url)
        Folder.create(file_path)
        assert File.exists(os.path.join(file_path_default, file_name))
        File.download_file(file_name, url, file_path)
        assert File.exists(os.path.join(file_path, file_name))
