import os
import time
import unittest
from os.path import expanduser
from random import randint

from nose.tools import timed

from core.base_test.run_context import TestContext
from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.perf_utils import PerfUtils
from core.utils.process import Run, Process
from core.utils.wait import Wait


# noinspection PyMethodMayBeStatic
class ProcessTests(unittest.TestCase):

    def tearDown(self):
        for process in TestContext.STARTED_PROCESSES:
            Log.info("Kill Process: " + os.linesep + process.commandline)
            Process.kill_pid(process.pid)

    def test_01_run_simple_command(self):
        home = expanduser("~")
        result = Run.command(cmd='ls ' + home)
        assert result.exit_code == 0, 'Wrong exit code of successful command.'
        assert result.log_file is None, 'No log file should be generated if wait=True.'
        assert result.complete is True, 'Complete should be true when process execution is complete.'
        assert result.duration < 1, 'Process duration took too much time.'
        assert 'Desktop' in result.output, 'Listing home do not include Desktop folder.'

    @timed(5)
    @unittest.skipIf(Settings.HOST_OS is OSType.WINDOWS, 'tail is not available on Windows')
    def test_02_run_command_without_wait_for_completion(self):
        file_path = os.path.join(Settings.TEST_OUT_HOME, 'temp.txt')
        File.write(path=file_path, text='test')
        result = Run.command(cmd='tail -f ' + file_path, wait=False)
        time.sleep(1)
        assert result.exit_code is None, 'exit code should be None when command is not complete.'
        assert result.complete is False, 'tail command should not exit.'
        assert result.duration is None, 'duration should be None in case process is not complete'
        assert result.output is '', 'output should be empty string.'
        assert result.log_file is not None, 'stdout and stderr of tail command should be redirected to file.'
        assert 'test' in File.read(result.log_file), 'Log file should contains output of the command.'

    @timed(5)
    def test_10_wait(self):
        assert Wait.until(lambda: ProcessTests.seconds_are_odd(), timeout=10, period=0.01)
        assert Wait.until(lambda: ProcessTests.get_int() == 3, timeout=10, period=0.01)
        assert not Wait.until(lambda: False, timeout=1, period=0.01)

    @timed(5)
    def test_20_get_average_time(self):
        ls_time = PerfUtils.get_average_time(lambda: Run.command(cmd='ifconfig'), retry_count=5)
        assert 0.005 <= ls_time <= 0.025, "Command not executed in acceptable time. Actual value: " + str(ls_time)

    @staticmethod
    def seconds_are_odd():
        millis = int(round(time.time() * 1000))
        return millis % 2 == 0

    @staticmethod
    def get_int():
        return randint(1, 9)

    @staticmethod
    def ru():
        return randint(1, 9)


if __name__ == '__main__':
    unittest.main()
