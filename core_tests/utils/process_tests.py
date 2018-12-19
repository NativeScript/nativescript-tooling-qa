import time
import unittest

from core.utils.process import Process
from core.utils.run import run


class ProcessTests(unittest.TestCase):

    def test_30_kill_by_port(self):
        port = 4210
        self.start_server(port=port)
        time.sleep(0.5)
        running = Process.is_running_by_commandline(commandline='http.server')
        assert running, 'Failed to start simple http server.'
        Process.kill_by_port(port=port)
        time.sleep(0.5)
        running = Process.is_running_by_commandline(commandline='http.server')
        assert not running, 'Kill by port failed to kill process.'

    @staticmethod
    def start_server(port):
        run(cmd='python -m http.server ' + str(port), wait=False)


if __name__ == '__main__':
    unittest.main()
