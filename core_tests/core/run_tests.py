import os
import platform
import unittest
from os.path import expanduser

from core.settings import Settings
from core.utils.file_utils import File
from core.utils.process.run import run


# noinspection PyMethodMayBeStatic
@unittest.skipIf('Windows' in platform.platform(), 'This test class can not be exececuted on Windows OS.')
class RunPosixTests(unittest.TestCase):

    def test_01_run_simple_command(self):
        home = expanduser("~")
        result = run(cmd='ls ' + home, wait=True, timeout=1)
        assert result.exit_code == 0, 'Wrong exit code of successful command.'
        assert result.log_file is None, 'No log file should be generated if wait=True.'
        assert result.complete is True, 'Complete should be true when process execution is complete.'
        assert result.duration < 1, 'Process duration took too much time.'
        assert 'Desktop' in result.output, 'Listing home do not include Desktop folder.'

    def test_02_run_command_with_redirect(self):
        home = expanduser("~")
        out_file = os.path.join(Settings.TEST_OUT_HOME, 'log.txt')
        result = run(cmd='ls ' + home + ' > ' + out_file, wait=True, timeout=1)
        assert result.exit_code == 0, 'Wrong exit code of successful command.'
        assert result.log_file is None, 'No log file should be generated if wait=True.'
        assert result.complete is True, 'Complete should be true when process execution is complete.'
        assert result.duration < 1, 'Process duration took too much time.'
        assert result.output == '', 'Output should be empty.'
        assert 'Desktop' in File.read(path=out_file)

    def test_03_run_command_with_pipe(self):
        result = run(cmd='echo "test case" | wc -w ', wait=True, timeout=1)
        assert result.exit_code == 0, 'Wrong exit code of successful command.'
        assert result.log_file is None, 'No log file should be generated if wait=True.'
        assert result.complete is True, 'Complete should be true when process execution is complete.'
        assert result.duration < 1, 'Process duration took too much time.'
        assert result.output == '2', 'Output should be 2.'

    def test_10_run_command_with_wait_true_that_exceed_timeout(self):
        # noinspection PyBroadException
        try:
            run(cmd='sleep 3', wait=True, timeout=1, fail_safe=False)
            assert False, 'This line should not be executed, because the line above should raise an exception.'
        except Exception:
            pass

    def test_11_run_command_with_wait_true_and_fail_safe_that_exceed_timeout(self):
        result = run(cmd='sleep 3', wait=True, timeout=1, fail_safe=True)
        assert result.exit_code is None, 'Exit code on non completed programs should be None.'
        assert result.log_file is None, 'No log file should be generated if wait=True.'
        assert result.complete is False, 'Complete should be true when process execution is complete.'
        assert result.duration < 2, 'Process duration should be same as timeout.'
        assert result.output == '', 'No output for not completed programs.'
