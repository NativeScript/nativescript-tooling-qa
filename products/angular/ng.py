import logging
import os

from core.base_test.test_context import TestContext
from core.settings import Settings
from core.utils.file_utils import File, Folder
from core.utils.process import Process
from core.utils.run import run
from core.utils.wait import Wait

NS_SCHEMATICS = "@nativescript/schematics"


class NG(object):

    @staticmethod
    def exec_command(command, cwd=Settings.TEST_RUN_HOME, wait=True, verify=True):
        """
        Execute tns command.
        :param command: NG cli command.
        :param cwd: Current working directory of the command.
        :param wait: Wait until command complete.
        :param verify: If true and wait is also true it will check exit code of the command.
        :return: ProcessInfo object.
        :rtype: core.utils.process_info.ProcessInfo
        """
        cmd = '{0} {1}'.format(Settings.Executables.NG, command)
        result = run(cmd=cmd, cwd=cwd, wait=wait, log_level=logging.INFO)
        if verify and wait:
            assert result.exit_code == 0, 'ng command exit with non zero exit code.'
        return result

    @staticmethod
    def new(collection=NS_SCHEMATICS, project=Settings.AppName.DEFAULT, shared=False, sample=False, prefix=None,
            source_dir=None, theme=True, style=None, webpack=True):
        """
        Execute `ng new`
        :param collection: Schematics collection.
        :param project: Project name.
        :param shared: If true pass --shared flag.
        :param sample: If true pass --sample flag.
        :param prefix: The prefix to apply to generated selectors (default value is `app`)
        :param source_dir: The name of the source directory (default value is `src`)
        :param theme: If false pass --no-theme flag.
        :param style: If style is not None pass --style flag (default value is `css`)
        :param webpack: If false pass --no-webpack flag.
        :return: ProcessInfo object.
        :rtype: core.utils.process_info.ProcessInfo
        """

        # Ensure old app do not exists
        project_path = os.path.join(Settings.TEST_RUN_HOME, project)
        Folder.clean(project_path)

        # Generate ng new command
        command = 'new'
        if collection is not None:
            command = command + ' --collection={0}'.format(collection)
        command = command + ' ' + project
        if shared:
            command = command + ' --shared'
        if sample:
            command = command + ' --sample'
        if prefix is not None:
            command = command + ' --prefix={0}'.format(str(prefix))
        if source_dir is not None:
            command = command + ' --sourceDir={0}'.format(str(source_dir))
        if style is not None:
            command = command + ' --style={0}'.format(str(style))
        if not webpack:
            command = command + ' --no-webpack'
        if not theme:
            command = command + ' --no-theme'

        # Execute the command and add current app to context
        TestContext.TEST_APP_NAME = project
        return NG.exec_command(command)

    @staticmethod
    def add(project, schematics_package):
        """
        Execute `ng serve` inside project dir.
        :param project: Project name.
        :param schematics_package: Schematics package, for example: @nativescript/schemtics@next.
        :return: ProcessInfo object.
        :rtype: core.utils.process_info.ProcessInfo
        """
        project_path = os.path.join(Settings.TEST_RUN_HOME, project)
        result = NG.exec_command(command='add {0}'.format(schematics_package), cwd=project_path, wait=True)
        return result

    @staticmethod
    def serve(project=Settings.AppName.DEFAULT, prod=True):
        """
        Execute `ng serve` inside project dir.
        :param project: Project name.
        :param prod: If true passes `--prod` flag.
        :return: ProcessInfo object.
        :rtype: core.utils.process_info.ProcessInfo
        """
        project_path = os.path.join(Settings.TEST_RUN_HOME, project)
        command = 'serve'
        if prod:
            command = command + ' --prod'
        result = NG.exec_command(command=command, cwd=project_path, wait=False)
        compiled = Wait.until(lambda: 'Compiled successfully' in File.read(result.log_file))
        if not compiled:
            NG.kill()
        assert compiled, 'Failed to compile NG app at {0}'.format(project)
        return result

    @staticmethod
    def kill():
        """
        Kill ng cli processes.
        """
        Process.kill_by_commandline(cmdline=Settings.Executables.NG)
