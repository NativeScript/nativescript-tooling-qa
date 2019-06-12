"""
Test for `tns --version` command
"""
import re
import os

from core.base_test.tns_test import TnsTest
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
class VersionTests(TnsTest):

    def test_001_version(self):
        version = Tns.version()
        version_list = version.output.split(os.linesep)
        for element in version_list:
            match = re.compile("^\\d+\\.\\d+\\.\\d+(-\\S+)?$").match(element)
            if match:
                break
        assert match, "{0} is not a valid version.".format(version)
