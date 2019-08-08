import os
import unittest

from core.settings.Settings import TEST_RUN_HOME, AppName
from core.utils.file_utils import Folder, File

from data.templates import Template
from products.nativescript.preview_helpers import Preview
from products.nativescript.tns import Tns


class PreviewHelperTests(unittest.TestCase):
    current_folder = os.path.dirname(os.path.realpath(__file__))
    log = ""

    @classmethod
    def setUpClass(cls):
        Folder.clean(os.path.join(TEST_RUN_HOME, AppName.DEFAULT))
        Tns.create(app_name=AppName.DEFAULT, template=Template.HELLO_WORLD_JS.local_package, update=True)
        cls.log = File.read(Tns.preview(AppName.DEFAULT).log_file)

    def test_01_constants(self):
        url = Preview.get_url(output=self.log)
        assert 'nsplay://boot?instanceId=' in url


if __name__ == '__main__':
    unittest.main()
