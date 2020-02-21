"""
Test for package-manager command
"""
from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from data.templates import Template
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
class PackageManagerTests(TnsTest):
    app_name = Settings.AppName.DEFAULT

    def setUp(self):
        Tns.exec_command(command='package-manager set npm')

    def test_001_package_manager_get(self):
        result = Tns.exec_command(command='package-manager get')
        assert result.exit_code == 0, 'tns package-manager get exit with non zero exit code.'
        assert 'npm' in result.output, 'Default package manager is not npm.'

    def test_002_package_manager_set(self):
        result = Tns.exec_command(command='package-manager set npm')
        assert result.exit_code == 0, 'tns package-manager set exit with non zero exit code.'
        assert "You've successfully set npm as your package manager" in result.output, \
            'tns package-manager set output is not correct.'

    def test_200_package_manager_yarn(self):
        result = Tns.exec_command(command='package-manager set yarn')
        assert result.exit_code == 0, 'tns package-manager set exit with non zero exit code.'
        assert "You've successfully set yarn as your package manager" in result.output
        self.__create_and_build_app()

    def test_210_package_manager_pnpm(self):
        result = Tns.exec_command(command='package-manager set pnpm')
        assert result.exit_code == 0, 'tns package-manager set exit with non zero exit code.'
        assert "You've successfully set pnpm as your package manager" in result.output
        self.__create_and_build_app()

    def test_300_package_manager(self):
        result = Tns.exec_command(command='package-manager get')
        assert result.exit_code == 0, 'tns package-manager get exit with non zero exit code.'
        assert 'Your current package manager is npm.' in result.output

    def test_310_package_manager_get_help(self):
        result = Tns.exec_command(command='package-manager get --help')
        assert result.exit_code == 0, 'tns package-manager get --help exit with non zero exit code.'
        assert 'Prints the value of the current package manager' in result.output

    def test_320_package_manager_set_help(self):
        result = Tns.exec_command(command='package-manager set --help')
        assert result.exit_code == 0, 'tns package-manager set --help exit with non zero exit code.'
        assert 'Enables the specified package manager for the NativeScript CLI' in result.output
        assert 'Supported values are npm, yarn and pnpm' in result.output

    def test_400_package_manager_set_wrong_value(self):
        result = Tns.exec_command(command='package-manager set fake')
        assert result.exit_code != 0, 'tns package-manager should exit with non zero exit code on fails.'
        assert 'fake is not a valid package manager.' in result.output, 'Wrong package manager not detected.'
        assert 'Supported values are: npm, pnpm, yarn.' in result.output, 'No message for supported managers.'

    def __create_and_build_app(self):
        Tns.create(app_name=self.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS == OSType.OSX:
            Tns.platform_add_ios(app_name=self.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        Tns.build_android(self.app_name)
        if Settings.HOST_OS != OSType.OSX:
            Tns.build_ios(self.app_name)
