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
        return Run.command(cmd=cmd, wait=wait)

    @staticmethod
    def new(collection=None, project=Settings.AppName.DEFAULT, shared=True, sample=False):
        """
        Execute `ng new`
        :param collection: Schematics collection.
        :param project: Project name.
        :param shared: If true pass --shared flag.
        :param sample: If true pass --sample flag.
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
        return NG.exec_command(command)

    @staticmethod
    def kill():
        """
        Kill ng cli processes.
        """
        Process.kill_by_commandline(cmdline=Settings.Executables.NG)
