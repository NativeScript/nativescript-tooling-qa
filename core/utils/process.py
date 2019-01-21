# pylint: disable=wrong-import-order
# pylint: disable=broad-except
import logging
import os

import psutil
import time

from core.base_test.test_context import TestContext
from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings


# noinspection PyBroadException,PyUnusedLocal
class Process(object):
    @staticmethod
    def is_running(pid):
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    @staticmethod
    def is_running_by_name(proc_name):
        """
        Check if process is running.
        """
        result = False
        for proc in psutil.process_iter():
            if proc_name in str(proc):
                result = True
                break
        return result

    @staticmethod
    def is_running_by_commandline(commandline):
        """
        Check if process with specified commandline is running.
        """
        proc = Process.get_proc_by_commandline(commandline=commandline)
        return bool(proc is not None)

    @staticmethod
    def get_proc_by_commandline(commandline):
        """
        Get process by commandline.
        :param commandline: Sub string of process commandline.
        :return: Process.
        """
        result = None
        for proc in psutil.process_iter():
            cmdline = ""
            try:
                cmdline = str(proc.cmdline())
            except Exception:
                continue
            if commandline in cmdline:
                result = proc
                break
        return result

    @staticmethod
    def wait_until_running(proc_name, timeout=60):
        """
        Wait until process is running
        :param proc_name: Process name.
        :param timeout: Timeout in seconds.
        :return: True if running, false if not running.
        """
        running = False
        end_time = time.time() + timeout
        while not running:
            time.sleep(5)
            running = Process.is_running_by_name(proc_name)
            if running:
                running = True
                break
            if (running is False) and (time.time() > end_time):
                error = "{0} not running in {1} seconds.", proc_name, timeout
                if Settings.PYTHON_VERSION < 2:
                    raise Exception(error)
                else:
                    raise TimeoutError(error)
        return running

    @staticmethod
    def kill(proc_name, proc_cmdline=None):
        if Settings.HOST_OS is OSType.WINDOWS:
            proc_name += ".exe"
        result = False
        for proc in psutil.process_iter():
            name = ""
            cmdline = ""
            try:
                name = str(proc.name())
                cmdline = str(proc.cmdline())
            except Exception:
                continue
            if proc_name == name:
                if Settings.HOST_OS == OSType.WINDOWS:
                    cmdline = cmdline.replace('\\\\', '\\')
                if (proc_cmdline is None) or (proc_cmdline is not None and proc_cmdline in cmdline):
                    try:
                        proc.kill()
                        Log.log(level=logging.DEBUG, msg="Process {0} has been killed.".format(proc_name))
                        result = True
                    except psutil.NoSuchProcess:
                        continue
        return result

    @staticmethod
    def kill_by_commandline(cmdline):
        result = False
        for proc in psutil.process_iter():
            cmd = ""
            try:
                cmd = str(proc.cmdline())
            except Exception:
                continue
            if cmdline in cmd:
                try:
                    proc.kill()
                    Log.log(level=logging.DEBUG, msg="Process {0} has been killed.".format(cmdline))
                    result = True
                except psutil.NoSuchProcess:
                    continue
        return result

    @staticmethod
    def kill_by_port(port):
        for proc in psutil.process_iter():
            try:
                connections = proc.connections(kind='inet')
                if connections:
                    for connection in connections:
                        if connection.laddr.port == port:
                            cmd = ''.join(proc.cmdline())
                            proc.kill()
                            Log.info('Kill processes listening on port {0}.'.format(str(port)))
                            Log.debug('Kill process: ' + cmd)
            except Exception:
                pass

    @staticmethod
    def kill_pid(pid):
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            Log.log(level=logging.DEBUG, msg="Process has been killed: {0}{1}".format(os.linesep, proc.cmdline()))
        except Exception:
            pass

    @staticmethod
    def kill_by_handle(file_path):
        for proc in psutil.process_iter():
            try:
                for item in proc.open_files():
                    if file_path in item.path:
                        Log.debug("{0} is locked by {1}".format(file_path, proc.name()))
                        Log.debug("Proc cmd: {0}".format(proc.cmdline()))
                        proc.kill()
            except Exception:
                continue

    @staticmethod
    def kill_all_in_context():
        for process in TestContext.STARTED_PROCESSES:
            name = process.commandline.split(' ')[0]
            Process.kill(proc_name=name, proc_cmdline=Settings.TEST_RUN_HOME)
