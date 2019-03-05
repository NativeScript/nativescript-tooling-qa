"""
File and Folder utils.
"""
import errno
import os
import shutil
import tarfile

from core.log.log import Log
from core.settings import Settings


class Folder(object):
    @staticmethod
    def clean(folder):
        if Folder.exists(folder=folder):
            Log.debug("Clean folder: " + folder)
            shutil.rmtree(folder, ignore_errors=True)

    @staticmethod
    def exists(folder):
        return os.path.isdir(folder)

    @staticmethod
    def is_empty(folder):
        return not os.listdir(folder)

    @staticmethod
    def create(folder):
        Log.debug("Create folder: " + folder)
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except OSError:
                raise

    @staticmethod
    def copy(source, target, clean_target=True, only_files=False):
        """
        Copy folders.
        :param source: Source folder.
        :param target: Target folder.
        :param clean_target: If True clean target folder before copy.
        :param only_files: If True only the files from source folder are copied to target folder.
        """
        if clean_target:
            Folder.clean(folder=target)
        Log.info('Copy {0} to {1}'.format(source, target))
        if only_files is True:
            files = os.listdir(source)

            for f in files:
                f_path = os.path.join(source, f)
                File.copy(f_path, target)
        else:
            try:
                shutil.copytree(source, target)
            except OSError as exc:
                if exc.errno == errno.ENOTDIR:
                    shutil.copy(source, target)
                else:
                    raise

    @staticmethod
    def get_size(folder):
        """
        Get folder size in bytes.
        :param folder: Folder path.
        :return: Size in bytes.
        """
        # pylint: disable=unused-variable
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder):
            for file_name in filenames:
                file_path = os.path.join(dirpath, file_name)
                total_size += os.path.getsize(file_path)
        return total_size


# noinspection PyUnresolvedReferences
class File(object):
    @staticmethod
    def read(path):
        if File.exists(path):
            if Settings.PYTHON_VERSION < 3:
                with open(path, 'r') as file_to_read:
                    output = file_to_read.read()
                return str(output.decode('utf8').encode('utf8'))
            else:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    output = f.read()
                return output
        else:
            raise IOError("{0} not found!".format(path))

    @staticmethod
    def write(path, text):
        if Settings.PYTHON_VERSION < 3:
            with open(path, 'w+') as text_file:
                text_file.write(text)
        else:
            with open(path, 'w+', encoding='utf-8', errors='ignore') as text_file:
                text_file.write(text)

    @staticmethod
    def append(path, text):
        if Settings.PYTHON_VERSION < 3:
            with open(path, 'a') as text_file:
                text_file.write(text)
        else:
            with open(path, 'a', encoding='utf-8', errors='ignore') as text_file:
                text_file.write(text)

    @staticmethod
    def replace(path, old_string, new_string):
        content = File.read(path=path)
        assert old_string in content, 'Can not find "{0}" in {1}'.format(old_string, path)
        new_content = content.replace(old_string, new_string)
        File.write(path=path, text=new_content)
        Log.info("")
        Log.info("##### REPLACE FILE CONTENT #####")
        Log.info("File: {0}".format(path))
        Log.info("Old String: {0}".format(old_string))
        Log.info("New String: {0}".format(new_string))
        Log.info("")

    @staticmethod
    def exists(path):
        return os.path.isfile(path)

    @staticmethod
    def copy(src, target):
        shutil.copy(src, target)
        Log.info('Copy {0} to {1}'.format(os.path.abspath(src), os.path.abspath(target)))

    @staticmethod
    def delete(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            Log.debug('Error: %s file not found' % path)

    @staticmethod
    def clean(path):
        if os.path.isfile(path):
            File.write(path, text='')
        else:
            raise IOError('Error: %s file not found' % path)

    @staticmethod
    def find_by_extension(folder, extension):
        """
        Find by file extension recursively.
        :param folder: Base folder where search is done.
        :param extension: File extension.
        :return: List of found files.
        """
        # pylint: disable=unused-variable
        matches = []
        if '.' not in extension:
            extension = '.' + extension
        for root, dirs, files in os.walk(folder):
            for f in files:
                if f.endswith(extension):
                    Log.debug('File with {0} extension found: {1}'.format(extension, os.path.abspath(f)))
                    matches.append(os.path.join(root, f))
        return matches

    @staticmethod
    def extract_part_of_text(text, key_word):
        """
        That method will extract text from last occurance of key word
        to the end of the file
        """
        index = text.rfind(key_word)
        text = text[index:]
        return text

    @staticmethod
    def unpack_tar(file_path, dest_dir):
        # noinspection PyBroadException
        try:
            tar_file = tarfile.open(file_path, 'r:gz')
            tar_file.extractall(dest_dir)
        # pylint: disable=broad-except
        except Exception:
            Log.debug('Failed to unpack .tar file {0}'.format(file_path))
