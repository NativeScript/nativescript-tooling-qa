import os
import time
import unittest
from os.path import expanduser

from nose.tools import timed

from core.settings import Settings
from core.utils.file_utils import File
from core.utils.process import Process
from core.utils.run import run


# noinspection PyMethodMayBeStatic
class RunTests(unittest.TestCase):

    def tearDown(self):
        Process.kill_all_in_context()

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

    @timed(5)
    def test_20_run_long_living_process(self):
        file_path = os.path.join(Settings.TEST_OUT_HOME, 'temp.txt')
        File.write(path=file_path, text='test')
        result = run(cmd='tail -f ' + file_path, wait=False)
        time.sleep(1)
        Process.kill_pid(pid=result.pid)
        assert result.exit_code is None, 'exit code should be None when command is not complete.'
        assert result.complete is False, 'tail command should not exit.'
        assert result.duration is None, 'duration should be None in case process is not complete'
        assert result.output is '', 'output should be empty string.'
        assert result.log_file is not None, 'stdout and stderr of tail command should be redirected to file.'
        assert 'tail' in File.read(result.log_file), 'Log file should contains cmd of the command.'
        assert 'test' in File.read(result.log_file), 'Log file should contains output of the command.'

    @timed(30)
    def test_40_run_npm_pack(self):
        package = 'tns-core-modules'
        version = '5.0.0'
        tarball = '{0}-{1}.tgz'.format(package, version)
        path = os.path.join(Settings.TEST_SUT_HOME, tarball)
        File.delete(path)
        result = run(cmd='npm pack https://registry.npmjs.org/{0}/-/{1}'.format(package, tarball),
                     cwd=Settings.TEST_SUT_HOME, wait=True)
        assert File.exists(path)
        assert tarball in result.output
        assert '=== Tarball Contents ===' in result.output
