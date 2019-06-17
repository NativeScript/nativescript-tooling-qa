import os

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.file_utils import Folder, File
from core.utils.npm import Npm
from data.templates import Template
from products.nativescript.app import App
from products.nativescript.tns import Tns

# APP_NAME = Settings.AppName.DEFAULT

class InitAndInstallTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    APP_PATH = os.path.join(Settings.TEST_RUN_HOME, app_name)

    def setUp(self):
        TnsTest.setUp(self)
        Folder.clean(self.APP_PATH)

    def test_204_install_defaults(self):
        # self.test_202_init_path()
        Tns.create(app_name=self.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        result = Tns.exec_command(command='install', path=self.APP_PATH)
        self.verify_installed(output=result.output)

    def test_205_install_external_packages(self):
        # self.test_202_init_path()
        Tns.create(app_name=self.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        # Add packages
        Npm.install(package='lodash', option='--save', folder=self.APP_PATH)
        Npm.install(package='gulp', option='--save-dev', folder=self.APP_PATH)
        assert App.is_dependency(app_name=self.app_name, dependency='lodash')
        assert App.is_dev_dependency(app_name=self.app_name, dependency='gulp')

        # Clean node modules
        Folder.clean(os.path.join(self.APP_PATH, 'node_modules'))
        Folder.clean(os.path.join(self.APP_PATH, 'platforms'))

        # Install and verify common packages
        result = Tns.exec_command(command='install', path=self.APP_PATH)
        self.verify_installed(output=result.output)

        # Verify external packages are also installed
        assert Folder.exists(os.path.join(self.APP_PATH, 'node_modules', 'lodash'))
        assert Folder.exists(os.path.join(self.APP_PATH, 'node_modules', 'gulp'))

    def test_300_install_and_prepare(self):
        # self.test_202_init_path()
        Tns.create(app_name=self.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        # Add packages
        Npm.install(package='lodash', option='--save', folder=self.APP_PATH)
        Npm.install(package='gulp', option='--save-dev', folder=self.APP_PATH)
        assert App.is_dependency(app_name=self.app_name, dependency='lodash')
        assert App.is_dev_dependency(app_name=self.app_name, dependency='gulp')

        # Call install and verify it do not fail if everything is already installed
        result = Tns.exec_command(command='install', path=self.APP_PATH)
        self.verify_installed(output=result.output)
        assert Folder.exists(os.path.join(self.APP_PATH, 'node_modules', 'lodash'))
        assert Folder.exists(os.path.join(self.APP_PATH, 'node_modules', 'gulp'))

        # Copy app folder and app resources
        Folder.copy(source=os.path.join(Settings.TEST_RUN_HOME, 'assets', 'apps', 'test-app-js-41', 'app'),
                    target=os.path.join(self.APP_PATH, 'app'))

        # Prepare project
        Tns.prepare_android(app_name=self.app_name)
        if Settings.HOST_OS == OSType.OSX:
            Tns.prepare_ios(app_name=self.app_name)

    def test_400_install_in_not_existing_folder(self):
        result = Tns.exec_command(command='install', path=self.app_name)
        assert "No project found" in result.output

    def verify_installed(self, output):
        # Verify output
        assert 'Copying template files' in output
        assert 'Platform android successfully added' in output
        if Settings.HOST_OS == OSType.OSX:
            assert 'Platform ios successfully added' in output

        # Verify files
        assert Folder.exists(os.path.join(self.APP_PATH, 'node_modules', 'tns-core-modules'))
        assert Folder.exists(os.path.join(self.APP_PATH, 'platforms', 'android'))
        assert File.exists(os.path.join(self.APP_PATH, 'platforms', 'android', 'build.gradle'))
        if Settings.HOST_OS == OSType.OSX:
            assert Folder.exists(os.path.join(self.APP_PATH, 'platforms', 'ios'))
            assert Folder.exists(os.path.join(self.APP_PATH, 'platforms', 'ios', 'TestApp.xcodeproj'))

        # App resources not created, see https://github.com/NativeScript/nativescript-cli/issues/4341
