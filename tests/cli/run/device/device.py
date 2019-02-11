"""
Tests for `tns devices` command
"""
import os
import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.settings import Settings
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
class TnsDeviceTests(TnsRunTest):
    PATH = os.environ.get('PATH')
    ANDROID_HOME = os.environ.get('ANDROID_HOME')

    def setUp(self):
        TnsRunTest.setUp(self)
        os.environ['PATH'] = self.PATH
        os.environ['ANDROID_HOME'] = self.ANDROID_HOME

    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, 'Skip on Windows machines.')
    def test_400_list_devices_without_android_sdk(self):
        path_without_android = ''
        for path in self.PATH.split(':'):
            if self.ANDROID_HOME not in path:
                path_without_android = path_without_android + path + ':'
        os.environ['PATH'] = path_without_android
        os.environ['ANDROID_HOME'] = 'WRONG_PATH'
        result = Tns.exec_command(command='devices')
        assert self.emu.name in result.output
        assert self.emu.id in result.output
        assert self.sim.name in result.output
        assert self.sim.id in result.output
