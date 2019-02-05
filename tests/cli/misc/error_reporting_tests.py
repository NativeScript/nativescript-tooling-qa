"""
Test for error-reporting command
"""
from core.base_test.tns_test import TnsTest
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
class ErrorReportingTests(TnsTest):

    def test_001_error_reporting_enable(self):
        result = Tns.exec_command(command='error-reporting enable')
        assert 'Error reporting is now enabled.' in result.output
        result = Tns.exec_command(command='error-reporting status')
        assert 'Error reporting is enabled.' in result.output

    def test_002_error_reporting_disable(self):
        result = Tns.exec_command(command='error-reporting disable')
        assert 'Error reporting is now disabled.' in result.output
        result = Tns.exec_command(command='error-reporting status')
        assert 'Error reporting is disabled.' in result.output

    def test_401_error_reporting_with_invalid_parameter(self):
        result = Tns.exec_command(command='error-reporting fake')
        assert "The value 'fake' is not valid" in result.output
        assert "Valid values are 'enable', 'disable' and 'status'." in result.output
