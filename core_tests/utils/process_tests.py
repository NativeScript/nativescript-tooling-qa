import time
import unittest
from random import randint

from nose.tools import timed

from core.utils.perf_utils import PerfUtils
from core.utils.process import Process
from core.utils.run import run
from core.utils.wait import Wait


# noinspection PyMethodMayBeStatic
class ProcessTests(unittest.TestCase):

    @timed(5)
    def test_10_wait(self):
        assert Wait.until(lambda: ProcessTests.seconds_are_odd(), timeout=10, period=0.01)
        assert Wait.until(lambda: ProcessTests.get_int() == 3, timeout=10, period=0.01)
        assert not Wait.until(lambda: False, timeout=1, period=0.01)

    @timed(5)
    def test_20_get_average_time(self):
        ls_time = PerfUtils.get_average_time(lambda: run(cmd='ifconfig'), retry_count=5)
        assert 0.005 <= ls_time <= 0.025, "Command not executed in acceptable time. Actual value: " + str(ls_time)

    def test_30_kill_by_port(self):
        Process.kill_by_port(port=4200)

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
