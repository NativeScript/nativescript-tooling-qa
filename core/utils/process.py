import logging
import os
import shlex
import time
from datetime import datetime
from subprocess import Popen, PIPE

import psutil

from core.base_test.test_context import TestContext
from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.process_info import ProcessInfo


class Run(object):
    @staticmethod
    def command(cmd, cwd=Settings.TEST_RUN_HOME, wait=True, register_for_cleanup=True, timeout=600,
                log_level=logging.DEBUG):
        # Init result values
        log_file = None
        complete = False
        duration = None
        output = ''

        # Command settings
        if not wait:
            time_string = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            log_file = os.path.join(Settings.TEST_OUT_LOGS, 'command_{0}.txt'.format(time_string))
            File.write(path=log_file, text=cmd + os.linesep + '====>' + os.linesep)
            cmd = cmd + ' >> ' + log_file + ' 2>&1 &'

        # Execute command:
        Log.log(level=log_level, message='Execute command: ' + cmd)
        Log.log(level=logging.DEBUG, message='CWD: ' + cwd)
        if wait:
            start = time.time()
            if Settings.HOST_OS is OSType.WINDOWS:
                process = Popen(cmd, stdout=PIPE, bufsize=1, cwd=cwd, shell=True)
            else:
                args = shlex.split(cmd)
                process = Popen(args, stdout=PIPE, stderr=PIPE, cwd=cwd, shell=False)
            p = psutil.Process(process.pid)

            # TODO: On Windows we hang if command do not complete for specified time
            # See: https://stackoverflow.com/questions/2408650/why-does-python-subprocess-hang-after-proc-communicate
            if Settings.HOST_OS is not OSType.WINDOWS:
                try:
                    p.wait(timeout=timeout)
                except psutil.TimeoutExpired:
                    p.kill()
                    raise
            out, err = process.communicate()
            output = (str(out) + os.linesep + str(err)).rstrip()
            complete = True
            end = time.time()
            duration = end - start
        else:
            process = Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, cwd=cwd)

        # Get result
        pid = process.pid
        exit_code = process.returncode

        if wait:
            Log.log(level=log_level, message='OUTPUT: ' + os.linesep + output)
        else:
            Log.log(level=log_level, message='OUTPUT REDIRECTED: ' + log_file)

        result = ProcessInfo(cmd=cmd, pid=pid, exit_code=exit_code, output=output, log_file=log_file, complete=complete,
                             duration=duration)
        if psutil.pid_exists(result.pid) and register_for_cleanup:
            TestContext.STARTED_PROCESSES.append(result)
        return result


# noinspection PyBroadException,PyUnusedLocal
class Process(object):
    @staticmethod
    def is_running(proc_name):
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
        if proc is not None:
            return True
        else:
            return False

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
            running = Process.is_running(proc_name)
            if running:
                running = True
                break
            if (running is False) and (time.time() > end_time):
                raise NameError("{0} not running in {1} seconds.", proc_name, timeout)
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
                if (proc_cmdline is None) or (proc_cmdline is not None and proc_cmdline in cmdline):
                    try:
                        proc.kill()
                        Log.log(level=logging.DEBUG, message="Process {0} has been killed.".format(proc_name))
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
                    Log.log(level=logging.DEBUG, message="Process {0} has been killed.".format(cmdline))
                    result = True
                except psutil.NoSuchProcess:
                    continue
        return result

    @staticmethod
    def kill_pid(pid):
        try:
            p = psutil.Process(pid)
            p.terminate()
        except Exception:
            pass

    @staticmethod
    def kill_by_handle(file_path):
        for proc in psutil.process_iter():
            try:
                for item in proc.open_files():
                    if file_path in item.path:
                        print "{0} is locked by {1}".format(file_path, proc.name())
                        print "Proc cmd: {0}".format(proc.cmdline())
                        proc.kill()
            except Exception:
                continue
