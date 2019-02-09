import os

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.file_utils import Folder, File
from core.utils.npm import Npm
from products.nativescript.app import App
from products.nativescript.tns import Tns

APP_NAME = Settings.AppName.DEFAULT
APP_PATH = os.path.join(Settings.TEST_RUN_HOME, APP_NAME)


# noinspection PyMethodMayBeStatic
class InitAndInstallTests(TnsTest):

    def setUp(self):
        TnsTest.setUp(self)
        Folder.clean(APP_PATH)

    def test_201_init_defaults(self):
        Folder.create(APP_PATH)
        result = Tns.exec_command(command='init --force', cwd=APP_PATH)
        self.verify_initialized(output=result.output)

    def test_202_init_path(self):
        result = Tns.exec_command(command='init --force', path=APP_NAME)
        self.verify_initialized(output=result.output)

    def test_203_init_update_existing_file(self):
        self.test_202_init_path()

        # Modify existing file
        package_json = os.path.join(Settings.TEST_RUN_HOME, APP_NAME, 'package.json')
        File.replace(path=package_json, old_string=APP_NAME, new_string='QApp')
        assert 'QApp' in File.read(package_json)

        # Overwrite changes
        self.test_202_init_path()

    def test_204_install_defaults(self):
        self.test_202_init_path()
        result = Tns.exec_command(command='install', path=APP_PATH)
        self.verify_installed(output=result.output)

    def test_205_install_external_packages(self):
        self.test_202_init_path()

        # Add packages
        Npm.install(package='lodash', option='--save', folder=APP_PATH)
        Npm.install(package='gulp', option='--save-dev', folder=APP_PATH)
        assert App.is_dependency(app_name=APP_NAME, dependency='lodash')
        assert App.is_dev_dependency(app_name=APP_NAME, dependency='gulp')

        # Clean node modules
        Folder.clean(os.path.join(APP_PATH, 'node_modules'))
        Folder.clean(os.path.join(APP_PATH, 'platforms'))

        # Install and verify common packages
        result = Tns.exec_command(command='install', path=APP_PATH)
        self.verify_installed(output=result.output)

        # Verify external packages are also installed
        assert Folder.exists(os.path.join(APP_PATH, 'node_modules', 'lodash'))
        assert Folder.exists(os.path.join(APP_PATH, 'node_modules', 'gulp'))

    def test_300_install_and_prepare(self):
        self.test_202_init_path()

        # Add packages
        Npm.install(package='lodash', option='--save', folder=APP_PATH)
        Npm.install(package='gulp', option='--save-dev', folder=APP_PATH)
        assert App.is_dependency(app_name=APP_NAME, dependency='lodash')
        assert App.is_dev_dependency(app_name=APP_NAME, dependency='gulp')

        # Call install and verify it do not fail if everything is already installed
        result = Tns.exec_command(command='install', path=APP_PATH)
        self.verify_installed(output=result.output)
        assert Folder.exists(os.path.join(APP_PATH, 'node_modules', 'lodash'))
        assert Folder.exists(os.path.join(APP_PATH, 'node_modules', 'gulp'))

        # Copy app folder and app resources
        Folder.copy(source=os.path.join(Settings.TEST_RUN_HOME, 'assets', 'template-min', 'app'),
                    target=os.path.join(APP_PATH, 'app'))

        # Prepare project
        Tns.prepare_android(app_name=APP_NAME)
        if Settings.HOST_OS == OSType.OSX:
            Tns.prepare_ios(app_name=APP_NAME)

        # Verify prepare
        base_path = os.path.join(APP_PATH, 'platforms', 'android', 'app', 'src', 'main', 'assets', 'app', 'tns_modules')
        assert Folder.exists(os.path.join(base_path, 'lodash')), 'Dependency not available in platforms.'
        assert not Folder.exists(os.path.join(base_path, 'gulp')), 'DevDependency available in platforms.'
        # TODO: Verify prepare for iOS

    def test_400_install_in_not_existing_folder(self):
        result = Tns.exec_command(command='install', path=APP_NAME)
        assert "No project found" in result.output

    def verify_initialized(self, output):
        # Verify output
        assert 'Project successfully initialized.' in output

        # Verify app folder do not exists
        assert not Folder.exists(os.path.join(APP_PATH, 'app'))
        assert not Folder.exists(os.path.join(APP_PATH, 'src'))
        assert not Folder.exists(os.path.join(APP_PATH, 'node_modules'))
        assert not Folder.exists(os.path.join(APP_PATH, 'platforms'))

        # Verify package.json
        json = App.get_package_json(app_name=APP_NAME)
        assert json['nativescript']['id'] == 'org.nativescript.{0}'.format(APP_NAME)
        assert json['nativescript']['tns-android']['version'] is not None
        if Settings.HOST_OS == OSType.OSX:
            assert json['nativescript']['tns-ios']['version'] is not None
        assert json['dependencies']['tns-core-modules'] is not None

    def verify_installed(self, output):
        # Verify output
        assert 'Copying template files' in output
        assert 'Platform android successfully added' in output
        if Settings.HOST_OS == OSType.OSX:
            assert 'Platform ios successfully added' in output

        # Verify files
        assert Folder.exists(os.path.join(APP_PATH, 'node_modules', 'tns-core-modules'))
        assert Folder.exists(os.path.join(APP_PATH, 'platforms', 'android'))
        assert File.exists(os.path.join(APP_PATH, 'platforms', 'android', 'build.gradle'))
        if Settings.HOST_OS == OSType.OSX:
            assert Folder.exists(os.path.join(APP_PATH, 'platforms', 'ios'))
            assert Folder.exists(os.path.join(APP_PATH, 'platforms', 'ios', 'TestApp.xcodeproj'))

        # App resources not created, see https://github.com/NativeScript/nativescript-cli/issues/4341
