"""
Test that check CLI package after installation.
"""
import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.run import run


class SetupTests(TnsTest):

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Skip on Linux and Windows')
    def test_300_mac_script_has_execution_permissions(self):
        script = os.path.join(Settings.TEST_RUN_HOME,
                              'node_modules', 'nativescript', 'setup', 'mac-startup-shell-script.sh')
        result = run(cmd='ls -la {0}'.format(script))
        assert '-rwxr-xr-x' in result.output, 'macOS script has not execution permissions.'
