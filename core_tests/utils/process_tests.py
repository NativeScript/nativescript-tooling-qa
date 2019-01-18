import unittest

import time

from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.process import Process
from core.utils.run import run


class ProcessTests(unittest.TestCase):
    if Settings.HOST_OS == OSType.WINDOWS:
        http_module = 'http.server'
    else:
        http_module = 'SimpleHTTPServer'

    def test_30_kill_by_port(self):
        port = 4210
        self.start_server(port=port)
        time.sleep(0.5)
        running = Process.is_running_by_commandline(commandline=self.http_module)
        assert running, 'Failed to start simple http server.'
        Process.kill_by_port(port=port)
        time.sleep(0.5)
        running = Process.is_running_by_commandline(commandline=self.http_module)
        assert not running, 'Kill by port failed to kill process.'

    def start_server(self, port):
        run(cmd='python -m {0} {1}'.format(self.http_module, str(port)), wait=False)


if __name__ == '__main__':
    unittest.main()
