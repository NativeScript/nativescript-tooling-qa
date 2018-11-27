"""
File and Folder utils.
"""
import errno
import os
import shutil
import stat

from core.log.log import Log


class Folder(object):
    @staticmethod
    def clean(folder):
        if Folder.exists(folder=folder):
            Log.debug("Clean folder: " + folder)
            try:
                shutil.rmtree(folder)
            except OSError as e:
                for root, dirs, files in os.walk(folder, topdown=False):
                    for name in files:
                        filename = os.path.join(root, name)
                        os.chmod(filename, stat.S_IWUSR)
                        os.remove(filename)
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(folder)
                Log.error('Error: %s - %s.' % (e.filename, e.strerror))

    @staticmethod
    def exists(folder):
        return os.path.isdir(folder)

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
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size


class File(object):
    @staticmethod
    def read(path, log_content=False):
        if File.exists(path):
            with open(path, 'r') as file_to_read:
                output = file_to_read.read()
            if log_content:
                Log.info('Read ' + path + ':')
                Log.info(output)
            return output
        else:
            raise IOError("{0} not found!".format(path))

    @staticmethod
    def write(path, text):
        with open(path, 'w+') as text_file:
            text_file.write(text)

    @staticmethod
    def replace(path, old_string, new_string):
        content = File.read(path=path)
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
    def clean(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            Log.debug('Error: %s file not found' % path)

    @staticmethod
    def find_by_extension(folder, extension):
        """
        Find by file extension recursively.
        :param folder: Base folder where search is done.
        :param extension: File extension.
        :return: List of found files.
        """
        matches = []
        if '.' not in extension:
            extension = '.' + extension
        for root, dirs, files in os.walk(folder):
            for f in files:
                if f.endswith(extension):
                    Log.debug('File with {0} extension found: {1}'.format(extension, os.path.abspath(f)))
                    matches.append(os.path.join(root, f))
        return matches
