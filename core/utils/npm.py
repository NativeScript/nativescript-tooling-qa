"""
A wrapper around npm commands.
"""
import os

from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.run import run
from core.utils.version import Version


class Npm(object):
    @staticmethod
    def run_npm_command(cmd, folder=Settings.TEST_RUN_HOME, verify=True):
        command = 'npm {0}'.format(cmd).strip()
        Log.info(command + " (at " + str(folder) + ").")
        result = run(cmd=command, cwd=folder, wait=True, timeout=300)
        if verify:
            assert result.exit_code == 0, '" + command + " exited with non zero exit code!: \n' + result.output
        return result.output.strip()

    @staticmethod
    def cache_clean():
        Npm.run_npm_command(cmd='cache clean -f')

    @staticmethod
    def version():
        version = Npm.run_npm_command(cmd='-v')
        return Version.get(version)

    @staticmethod
    def download(package, output_file):
        output = Npm.run_npm_command('view {0} dist.tarball'.format(package))
        assert '.tgz' in output, 'Failed to find tarball of {0} package.'.format(
            package)
        npm_package = output.split('/')[-1].split('\n')[0]
        src_file = os.path.join(Settings.TEST_SUT_HOME, npm_package)
        File.delete(path=output_file)
        Npm.run_npm_command('pack ' + output, folder=Settings.TEST_SUT_HOME)
        File.copy(source=src_file, target=output_file)
        File.delete(src_file)

    @staticmethod
    def pack(folder, output_file):
        Npm.run_npm_command('pack', folder=folder)
        src_file = File.find_by_extension(folder=folder, extension='tgz')[0]
        File.copy(source=src_file, target=output_file)
        File.delete(src_file)

    @staticmethod
    def install(package='', option='', folder=Settings.TEST_RUN_HOME):
        if package is None:
            raise NameError('Package can not be None.')
        command = 'i {0} {1}'.format(package, option)
        output = Npm.run_npm_command(command, folder=folder)
        assert 'ERR!' not in output, "`npm " + command + "` failed with: \n" + output
        return output

    @staticmethod
    def uninstall(package, option='', folder=Settings.TEST_RUN_HOME):
        if package is None or package == '':
            raise NameError('Package can not be None.')
        return Npm.run_npm_command(
            'un {0} {1}'.format(package, option), folder=folder)

    @staticmethod
    def get_version(package):
        return Npm.run_npm_command('show {0} version'.format(package))
