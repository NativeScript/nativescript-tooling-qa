import os

from core.base_test.tns_test import TnsTest
from core.settings.Settings import TEST_RUN_HOME
from core.utils.file_utils import File, Folder


# noinspection PyMethodMayBeStatic
class FileUtilsTests(TnsTest):

    def test_01_file_download(self):
        file_name = "nativescript-logo.png"
        file_path_default = TEST_RUN_HOME
        file_path = os.path.join(TEST_RUN_HOME, "test")
        url = "https://www.nativescript.org/images/default-source/logos/nativescript-logo.png"
        File.download(file_name, url)
        Folder.create(file_path)
        assert File.exists(os.path.join(file_path_default, file_name))
        File.download(file_name, url, file_path)
        assert File.exists(os.path.join(file_path, file_name))
