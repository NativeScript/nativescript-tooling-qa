import logging
import os
import time
from datetime import datetime

import psutil

from core.base_test.test_context import TestContext
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.process_info import ProcessInfo

if os.name == 'posix' and Settings.PYTHON_VERSION < 3:
    # Import subprocess32 on Posix when Python2 is detected
    # noinspection PyPackageRequirements
    import subprocess32 as subprocess
else:
    import subprocess


def run(cmd, cwd=Settings.TEST_RUN_HOME, wait=True, timeout=600, fail_safe=False, register=True,
        log_level=logging.DEBUG):
    # Init result values
    time_string = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    log_file = os.path.join(Settings.TEST_OUT_LOGS, 'command_{0}.txt'.format(time_string))
    complete = False
    duration = None
    output = ''

    # Command settings
    if not wait:
        File.write(path=log_file, text=cmd + os.linesep + '====>' + os.linesep)
        cmd = cmd + ' >> ' + log_file + ' 2>&1 &'

    # Log command that will be executed:
    Log.log(level=log_level, msg='Execute command: ' + cmd)
    Log.log(level=logging.DEBUG, msg='CWD: ' + cwd)

    # Execute command:
    if wait:
        start = time.time()
        with open(log_file, "w") as log:
            process = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=log)

        # Wait until command complete
        try:
            process.wait(timeout=timeout)
            complete = True
            out, err = process.communicate()
            if out is not None:
                output = str(out.decode('utf-8')).strip()
            if err is not None:
                output = os.linesep + str(err.decode('utf-8')).strip()
        except subprocess.TimeoutExpired:
            process.kill()
            if fail_safe:
                Log.error('Command "{0}" timeout after {1} seconds.'.format(cmd, timeout))
            else:
                raise
        output = output + File.read(path=log_file)
        File.clean(path=log_file)
        end = time.time()
        duration = end - start
    else:
        process = psutil.Popen(cmd, cwd=cwd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

    # Get result
    pid = process.pid
    exit_code = process.returncode

    # Log output of the process
    if wait:
        Log.log(level=log_level, msg='OUTPUT: ' + os.linesep + output)
    else:
        Log.log(level=log_level, msg='OUTPUT REDIRECTED: ' + log_file)

    # Construct result
    result = ProcessInfo(cmd=cmd, pid=pid, exit_code=exit_code, output=output, log_file=log_file, complete=complete,
                         duration=duration)

    # Register in TestContext
    if psutil.pid_exists(result.pid) and register:
        TestContext.STARTED_PROCESSES.append(result)

    # Return the result
    return result
