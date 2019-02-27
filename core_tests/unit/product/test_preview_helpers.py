import os
import unittest

from core.utils.file_utils import File
from products.nativescript.preview_helpers import Preview


# noinspection PyMethodMayBeStatic
class PreviewHelperTests(unittest.TestCase):
    current_folder = os.path.dirname(os.path.realpath(__file__))

    def test_01_constants(self):
        text = File.read(path=os.path.join(self.current_folder, 'preview.log'))
        url = Preview.get_url(output=text)
        assert 'nsplay://boot\\?instanceId=' in url


if __name__ == '__main__':
    unittest.main()
