import sys

import nose

import run_common
from core.log.log import Log

if __name__ == '__main__':
    run_common.prepare(clone_templates=True, install_ng_cli=False)
    Log.info("Running tests...")
    arguments = [
        'nosetests', '-v', '-s', '--nologcapture', '--with-doctest',
        '--with-xunit'
    ]
    for i in sys.argv:
        arguments.append(str(i))
    nose.run(argv=arguments)
