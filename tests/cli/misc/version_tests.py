"""
Test for `tns --version` command
"""
import re

from core.base_test.tns_test import TnsTest
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
class VersionTests(TnsTest):

    def test_001_version(self):
        version = Tns.version()
        match = re.compile("^\\d+\\.\\d+\\.\\d+(-\\S+)?$").match(version)
        assert match, "{0} is not a valid version.".format(version)
