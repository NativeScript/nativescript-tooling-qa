import os

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.file_utils import Folder
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
        for line in fileinput.input(self.app_name + "/package.json", inplace=1):
            print
            line.lower().replace(app_identifier, "org.nativescript.TestApp12"),
        output = File.read(self.app_name + "/package.json")
        print
        output
        assert "org.nativescript.TestApp12" in output

        # Overwrite changes
        self.test_202_init_path()

    def test_204_install_defaults(self):
        self.test_202_init_path()
        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/platforms/android/build.gradle")

        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TestApp.xcodeproj")

    def test_205_install_node_modules(self):
        self.test_202_init_path()

        if (USE_YARN == "True"):
            Npm.install(package="gulp", option="--dev", folder=BaseClass.app_name)
            Npm.install(package="lodash", folder=BaseClass.app_name)
        else:
            Npm.install(package="gulp", option="--save-dev", folder=BaseClass.app_name)
            Npm.install(package="lodash", option="--save", folder=BaseClass.app_name)

        output = File.read(self.app_name + "/package.json")
        assert devDependencies in output
        assert "gulp" in output
        assert "lodash" in output

        Folder.cleanup(self.app_name + '/platforms')
        assert not File.exists(self.app_name + "/platforms")
        Folder.cleanup(self.app_name + '/node_modules')
        assert not File.exists(self.app_name + "/node_modules")

        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/node_modules/lodash")
        assert File.exists(self.app_name + "/node_modules/gulp")

        assert File.exists(self.app_name + "/platforms/android/build.gradle")

        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TestApp.xcodeproj")

    def test_300_install_node_modules_if_node_modules_folder_exists(self):
        self.test_202_init_path()

        if (USE_YARN == "True"):
            Npm.install(package="gulp", option="--dev", folder=BaseClass.app_name)
            Npm.install(package="lodash", folder=BaseClass.app_name)
        else:
            Npm.install(package="gulp", option="--save-dev", folder=BaseClass.app_name)
            Npm.install(package="lodash", option="--save", folder=BaseClass.app_name)

        output = File.read(self.app_name + "/package.json")
        assert devDependencies in output
        assert "gulp" in output
        assert "lodash" in output

        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/node_modules/lodash")
        assert File.exists(self.app_name + "/node_modules/gulp")
        assert File.exists(self.app_name + "/platforms/android/build.gradle")
        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TestApp.xcodeproj")

    def test_301_install_and_prepare(self):
        self.test_202_init_path()
        Tns.platform_add_android(attributes={"--path": self.app_name}, version="next")

        Npm.install(package='', folder=BaseClass.app_name)
        if (USE_YARN == "True"):
            Npm.install(package="gulp", option="--dev", folder=BaseClass.app_name)
            Npm.install(package="lodash", folder=BaseClass.app_name)
        else:
            Npm.install(package="gulp", option="--save-dev", folder=BaseClass.app_name)
            Npm.install(package="lodash", option="--save", folder=BaseClass.app_name)

        source = os.path.join(SUT_FOLDER, "template-hello-world", "app")
        dest = os.path.join(self.app_name, "app")
        Folder.copy(source, dest)

        output = File.read(self.app_name + "/package.json")
        assert devDependencies in output
        assert "gulp" in output
        assert "lodash" in output

        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/node_modules/lodash")
        assert File.exists(self.app_name + "/node_modules/gulp")
        assert File.exists(self.app_name + "/platforms/android/build.gradle")

        Tns.prepare_android(attributes={"--path": self.app_name})
        assert File.exists(os.path.join(self.app_name, TnsAsserts.PLATFORM_ANDROID_NPM_MODULES_PATH, "lodash"))
        assert not File.exists(os.path.join(self.app_name, TnsAsserts.PLATFORM_ANDROID_NPM_MODULES_PATH, "gulp"))

        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TestApp.xcodeproj")
            Tns.prepare_ios(attributes={"--path": self.app_name})
            assert File.exists(os.path.join(self.app_name, TnsAsserts.PLATFORM_ANDROID_NPM_MODULES_PATH, "lodash"))
            assert not File.exists(os.path.join(self.app_name, TnsAsserts.PLATFORM_ANDROID_NPM_MODULES_PATH, "gulp"))

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
