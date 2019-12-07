import os
import unittest

from core.base_test.test_context import TestContext
from core.settings import Settings
from core.utils.file_utils import File, Folder


# noinspection PyMethodMayBeStatic
class FileUtilsTests(unittest.TestCase):
    current_folder = os.path.dirname(os.path.realpath(__file__))

    def test_01_read(self):
        logs = os.path.join(self.current_folder, 'resources', 'file.txt')
        assert 'Compiled successfully' in File.read(logs)

    def test_02_replace(self):
        # Path to files
        old_scss = os.path.join(self.current_folder, 'resources', 'app.android.scss')
        new_scss = os.path.join(self.current_folder, 'resources', 'app.android.add_style.scss')
        old_value = 'Android here'
        new_value = 'Android here\n.page { background-color: red;}'

        # Create new file (so we don't break original one).
        File.copy(source=old_scss, target=new_scss)
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

    def test_03_replace_with_restore(self):
        TestContext.BACKUP_FILES.clear()
        Folder.clean(Settings.BACKUP_FOLDER)

        # Path to files
        file_name = "app.android.add_style.scss"
        old_scss = os.path.join(self.current_folder, 'resources', 'app.android.scss')
        new_scss = os.path.join(self.current_folder, 'resources', file_name)
        old_value = 'Android here'
        new_value = 'Android here\n.page { background-color: red;}'

        # Create new file (so we don't break original one).
        File.copy(source=old_scss, target=new_scss)
        assert len(File.read(path=new_scss).splitlines()) == 14, 'Unexpected lines count.'

        # Replace
        File.replace(path=new_scss, old_string=old_value, new_string=new_value, backup_files=True)
        content = File.read(path=new_scss)
        assert 'red;' in content, 'Failed to replace string.'
        assert len(content.splitlines()) == 15, 'Unexpected lines count.'
        assert File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not backup!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(0) == new_scss, "File path is not correct!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(1) == file_name, "File name not correct!"

        # Revert
        TnsTest.restore_files()
        content = File.read(path=new_scss)
        assert 'red;' not in content, 'Failed to replace string.'
        assert len(content.splitlines()) == 14, 'Unexpected lines count.'
        assert not File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not deleted!"
        assert not TestContext.BACKUP_FILES, "File object not deleted!"

        File.delete(path=new_scss)

    def test_04_delete_with_restore(self):
        TestContext.BACKUP_FILES.clear()
        Folder.clean(Settings.BACKUP_FOLDER)

        # Path to files
        file_name = "app.android.add_style.scss"
        old_scss = os.path.join(self.current_folder, 'resources', 'app.android.scss')
        new_scss = os.path.join(self.current_folder, 'resources', file_name)

        # Create new file (so we don't break original one).
        File.copy(source=old_scss, target=new_scss)
        assert len(File.read(path=new_scss).splitlines()) == 14, 'Unexpected lines count.'

        # Replace
        File.delete(path=new_scss, backup_files=True)
        assert File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not backup!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(0) == new_scss, "File path is not correct!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(1) == file_name, "File name not correct!"

        # Revert
        TnsTest.restore_files()
        content = File.read(path=new_scss)
        assert len(content.splitlines()) == 14, 'Unexpected lines count.'
        assert not File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not deleted!"
        assert not TestContext.BACKUP_FILES, "File object not deleted!"

        File.delete(path=new_scss)

    def test_05_copy_to_folder_with_restore(self):
        TestContext.BACKUP_FILES.clear()
        Folder.clean(Settings.BACKUP_FOLDER)

        # Path to files
        file_name = "app.android.scss"
        folder_name = os.path.join(self.current_folder, 'resources', 'new')
        Folder.create(folder_name)
        old_scss = os.path.join(self.current_folder, 'resources', 'app.android.scss')
        new_scss = os.path.join(folder_name, file_name)

        # Test Copy
        File.copy(source=old_scss, target=folder_name, backup_files=True)
        assert File.exists(new_scss)
        assert len(File.read(path=new_scss).splitlines()) == 14, 'Unexpected lines count.'
        assert not File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File should not be backup!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(0) == new_scss, "File path is not correct!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(1) == file_name, "File name not correct!"

        # Revert
        TnsTest.restore_files()
        assert not File.exists(new_scss)
        assert not File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not deleted!"
        assert not TestContext.BACKUP_FILES, "File object not deleted!"

    def test_06_copy_to_not_existing_file_with_restore(self):
        TestContext.BACKUP_FILES.clear()
        Folder.clean(Settings.BACKUP_FOLDER)
        # Path to files
        file_name = "app.android.add_style.scss"
        folder_name = os.path.join(self.current_folder, 'resources', 'new')
        Folder.clean(folder_name)
        Folder.create(folder_name)
        old_scss = os.path.join(self.current_folder, 'resources', 'app.android.scss')
        new_scss = os.path.join(folder_name, file_name)

        # Test Copy
        File.copy(source=old_scss, target=new_scss, backup_files=True)
        assert File.exists(new_scss)
        assert len(File.read(path=new_scss).splitlines()) == 14, 'Unexpected lines count.'
        assert not File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not backup!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(0) == new_scss, "File path is not correct!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(1) == file_name, "File name not correct!"

        # Revert
        TnsTest.restore_files()
        assert not File.exists(new_scss)
        assert not File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not deleted!"
        assert not TestContext.BACKUP_FILES, "File object not deleted!"

    def test_07_copy_to_existing_file_with_restore(self):
        TestContext.BACKUP_FILES.clear()
        Folder.clean(Settings.BACKUP_FOLDER)

        # Path to files
        file_name = "app.android.add_style.scss"
        folder_name = os.path.join(self.current_folder, 'resources', 'new')
        Folder.clean(folder_name)
        Folder.create(folder_name)
        old_scss = os.path.join(self.current_folder, 'resources', 'app.android.scss')
        new_scss = os.path.join(folder_name, file_name)
        old_value = 'Android here'
        new_value = 'Android here\n.page { background-color: red;}'

        # Create new file (so we don't break original one).
        File.copy(source=old_scss, target=new_scss)
        assert len(File.read(path=new_scss).splitlines()) == 14, 'Unexpected lines count.'

        # Replace
        File.replace(path=new_scss, old_string=old_value, new_string=new_value)
        content = File.read(path=new_scss)
        assert 'red;' in content, 'Failed to replace string.'
        assert len(content.splitlines()) == 15, 'Unexpected lines count.'

        # Test Copy
        File.copy(source=old_scss, target=new_scss, backup_files=True)
        content = File.read(path=new_scss)
        assert 'red;' not in content, 'Failed to copy file!'
        assert len(content.splitlines()) == 14, 'Unexpected lines count.'
        assert File.exists(new_scss)
        assert File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not backup!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(0) == new_scss, "File path is not correct!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(1) == file_name, "File name not correct!"

        # Revert
        TnsTest.restore_files()
        assert File.exists(new_scss)
        content = File.read(path=new_scss)
        assert 'red;' in content, 'Failed to replace string.'
        assert len(content.splitlines()) == 15, 'Unexpected lines count.'
        assert not File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not deleted!"
        assert not TestContext.BACKUP_FILES, "File object not deleted!"

        File.delete(path=new_scss)

    def test_08_copy_to_two_files_same_name_with_restore(self):
        TestContext.BACKUP_FILES.clear()
        Folder.clean(Settings.BACKUP_FOLDER)

        # Path to files
        file_name = "app.android.add_style.scss"
        folder_name_new1 = os.path.join(self.current_folder, 'resources', 'new1')
        Folder.clean(folder_name_new1)
        Folder.create(folder_name_new1)
        folder_name_new2 = os.path.join(self.current_folder, 'resources', 'new2')
        Folder.clean(folder_name_new2)
        Folder.create(folder_name_new2)
        folder_name_new3 = os.path.join(self.current_folder, 'resources', 'new3')
        Folder.clean(folder_name_new3)
        Folder.create(folder_name_new3)
        folder_name_new4 = os.path.join(self.current_folder, 'resources', 'new4')
        Folder.clean(folder_name_new4)
        Folder.create(folder_name_new4)

        old_scss = os.path.join(self.current_folder, 'resources', 'app.android.scss')

        new_scss_new1 = os.path.join(folder_name_new1, file_name)
        new_scss_new2 = os.path.join(folder_name_new2, file_name)
        new_scss_new3 = os.path.join(folder_name_new3, file_name)
        new_scss_new4 = os.path.join(folder_name_new4, file_name)
        old_value = 'Android here'
        new_value_file1 = 'Android here\n.page { background-color: red;}'
        new_value_file2 = 'Android here\n.page { background-color: pink;}'

        # Create new file (so we don't break original one).
        File.copy(source=old_scss, target=new_scss_new1)
        File.copy(source=old_scss, target=new_scss_new2)
        File.copy(source=old_scss, target=new_scss_new3)
        File.copy(source=old_scss, target=new_scss_new4)
        assert len(File.read(path=new_scss_new1).splitlines()) == 14, 'Unexpected lines count.'
        assert len(File.read(path=new_scss_new2).splitlines()) == 14, 'Unexpected lines count.'
        assert len(File.read(path=new_scss_new3).splitlines()) == 14, 'Unexpected lines count.'
        assert len(File.read(path=new_scss_new4).splitlines()) == 14, 'Unexpected lines count.'

        # Replace
        File.replace(path=new_scss_new1, old_string=old_value, new_string=new_value_file1)
        File.replace(path=new_scss_new2, old_string=old_value, new_string=new_value_file2)
        content = File.read(path=new_scss_new1)
        assert 'red;' in content, 'Failed to replace string.'
        assert len(content.splitlines()) == 15, 'Unexpected lines count.'
        content = File.read(path=new_scss_new2)
        assert 'pink;' in content, 'Failed to replace string.'
        assert len(content.splitlines()) == 15, 'Unexpected lines count.'

        # Test Copy
        File.copy(source=new_scss_new1, target=new_scss_new3, backup_files=True)
        content = File.read(path=new_scss_new3)
        assert 'red;' in content, 'Failed to copy file!'
        assert len(content.splitlines()) == 15, 'Unexpected lines count.'
        assert File.exists(new_scss_new3)
        assert File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not backup!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(0) == new_scss_new3, "File path is not correct!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(1) == file_name, "File name not correct!"

        File.copy(source=new_scss_new2, target=new_scss_new4, backup_files=True)
        content = File.read(path=new_scss_new4)
        assert 'pink;' in content, 'Failed to copy file!'
        assert len(content.splitlines()) == 15, 'Unexpected lines count.'
        assert File.exists(new_scss_new3)
        assert File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not backup!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(0) == new_scss_new4, "File path is not correct!"
        assert TestContext.BACKUP_FILES.items()[0].__getitem__(1) == (file_name + "1"), "File name not correct!"

        # Revert
        TnsTest.restore_files()
        assert File.exists(new_scss_new3)
        content = File.read(path=new_scss_new3)
        assert 'red;' not in content, 'Failed to replace string.'
        assert len(content.splitlines()) == 14, 'Unexpected lines count.'
        assert not File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not deleted!"
        assert not TestContext.BACKUP_FILES, "File object not deleted!"
        assert File.exists(new_scss_new4)
        content = File.read(path=new_scss_new4)
        assert 'pink;' not in content, 'Failed to replace string.'
        assert len(content.splitlines()) == 14, 'Unexpected lines count.'
        assert not File.exists(os.path.join(Settings.BACKUP_FOLDER, file_name)), "File not deleted!"
        assert not TestContext.BACKUP_FILES, "File object not deleted!"

        Folder.clean(folder_name_new1)
        Folder.clean(folder_name_new2)
        Folder.clean(folder_name_new3)
        Folder.clean(folder_name_new4)


if __name__ == '__main__':
    unittest.main()
