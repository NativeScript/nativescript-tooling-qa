"""
Test for package-manager command
"""
from core.base_test.tns_test import TnsTest
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
class PackageManagerTests(TnsTest):

    def test_001_package_manager_get(self):
        result = Tns.exec_command(command='package-manager get')
        assert result.exit_code == 0, 'tns package-manager get exit with non zero exit code.'
        assert 'npm' in result.output, 'Default package manager is not npm.'

    def test_400_package_manager_set_wrong_value(self):
        result = Tns.exec_command(command='package-manager set fake')
        assert result.exit_code != 0, 'tns package-manager should exit with non zero exit code on fails.'
        assert 'fake is not a valid package manager.' in result.output, 'Wrong package manager not detected.'
        assert 'Supported values are: npm, pnpm, yarn.' in result.output, 'No message for supported managers.'
