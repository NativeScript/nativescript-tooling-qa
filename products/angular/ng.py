import logging

from core.settings import Settings
from core.utils.process import Run, Process

NS_SCHEMATICS = "@nativescript/schematics"


class NG(object):

    @staticmethod
    def exec_command(command, wait=True):
        """
        Execute tns command.
        :param command: NG cli command.
        :param wait: Wait until command complete.
        :return: ProcessInfo object.
        :rtype: core.utils.process_info.ProcessInfo
        """
        cmd = '{0} {1}'.format(Settings.Executables.NG, command)
        return Run.command(cmd=cmd, wait=wait, log_level=logging.INFO)

    @staticmethod
    def new(collection=NS_SCHEMATICS, project=Settings.AppName.DEFAULT, shared=True, sample=False, prefix=None,
            theme=True, style=None, webpack=True):
        """
        Execute `ng new`
        :param collection: Schematics collection.
        :param project: Project name.
        :param shared: If true pass --shared flag.
        :param sample: If true pass --sample flag.
        :param prefix: The prefix to apply to generated selectors (default value is `app`)
        :param theme: If false pass --no-theme flag.
        :param style: If style is not None pass --style flag (default value is `css`)
        :param webpack: If false pass --no-webpack flag.
        :return: ProcessInfo object.
        :rtype: core.utils.process_info.ProcessInfo
        """
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
        if style is not None:
            command = command + ' --style={0}'.format(str(style))
        if not webpack:
            command = command + ' --no-webpack'
        if not theme:
            command = command + ' --no-theme'
        return NG.exec_command(command)

    @staticmethod
    def kill():
        """
        Kill ng cli processes.
        """
        Process.kill_by_commandline(cmdline=Settings.Executables.NG)
