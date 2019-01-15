import os
import unittest

from core.settings import Settings
from core.utils.file_utils import File


# noinspection PyMethodMayBeStatic
class FileUtilsTests(unittest.TestCase):

    def test_01_read(self):
        logs = os.path.join(Settings.TEST_RUN_HOME, 'core_tests', 'utils', 'file.txt')
        assert 'Compiled successfully' in File.read(logs)

    def test_02_replace(self):
        # Path to files
        base_path = os.path.join(Settings.TEST_RUN_HOME, 'core_tests', 'utils')
        old_scss = os.path.join(base_path, 'app.android.scss')
        new_scss = os.path.join(base_path, 'app.android.add_style.scss')
        old_value = 'Android here'
        new_value = 'Android here\n.page { background-color: red;}'

        # Create new file (so we don't break original one).
        File.copy(src=old_scss, target=new_scss)
        assert len(File.read(path=new_scss).splitlines()) == 14, 'Unexpected lines count.'

        # Replace
        File.replace(path=new_scss, old_string=old_value, new_string=new_value)
        content = File.read(path=new_scss)
        assert 'red;' in content, 'Failed to replace string.'
        assert len(content.splitlines()) == 15, 'Unexpected lines count.'

        # Revert
        File.replace(path=new_scss, old_string=new_value, new_string=old_value)
        content = File.read(path=new_scss)
        assert 'red;' not in content, 'Failed to replace string.'
        assert len(content.splitlines()) == 14, 'Unexpected lines count.'

        File.delete(path=new_scss)


if __name__ == '__main__':
    unittest.main()
