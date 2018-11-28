import sys

import nose

import run_common
from core.log.log import Log

if __name__ == '__main__':
    run_common.prepare(shared=True)
    Log.info("Running tests...")
    arguments = ['nosetests', '-v', '-s', '--nologcapture', '--logging-filter=nose', '--with-xunit', '--with-flaky']
    for i in sys.argv:
        arguments.append(str(i))
    nose.run(argv=arguments)
