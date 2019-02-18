import os

from nose_parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.file_utils import Folder, File
from core.utils.git import Git
from data.apps import Apps
from data.templates import Template
from products.nativescript.app import App
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
class CreateTests(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)
        CreateTests.__clean_folders()

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        CreateTests.__clean_folders()

    def test_001_create_app_like_real_user(self):
        """Create app with no any params"""
        Tns.create(app_name=Settings.AppName.DEFAULT, app_data=Apps.HELLO_WORLD_JS, update=False)

    def test_002_create_app_template_js(self):
        """Create app with --template js project"""
        Tns.create(app_name=Settings.AppName.DEFAULT, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=Apps.HELLO_WORLD_JS, update=False)

    def test_003_create_app_template_ts(self):
        """Create app with --template ts project"""
        Tns.create(app_name=Settings.AppName.DEFAULT, template=Template.HELLO_WORLD_TS.local_package,
                   app_data=Apps.HELLO_WORLD_TS, update=False)

    def test_004_create_app_template_ng(self):
        """Create app with --template ng project"""
        Tns.create(app_name=Settings.AppName.DEFAULT, template=Template.HELLO_WORLD_NG.local_package,
                   app_data=Apps.HELLO_WORLD_NG, update=False)

    def test_005_create_project_with_path(self):
        """Create project with --path option"""
        Tns.create(app_name=Settings.AppName.DEFAULT,
                   template=Template.HELLO_WORLD_JS.local_package,
                   app_data=Apps.HELLO_WORLD_JS,
                   path=os.path.join(Settings.TEST_RUN_HOME, 'folder', 'subfolder'),
                   update=False)

    def test_006_create_project_with_dash(self):
        """ Create project with dash is possible, but packageId will skip the space symbol"""
        Tns.create(app_name=Settings.AppName.WITH_DASH, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=Apps.HELLO_WORLD_JS, update=False)

    def test_007_create_project_with_space(self):
        """ Create project with space is possible, but packageId will skip the dash symbol"""
        Tns.create(app_name=Settings.AppName.WITH_SPACE, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=Apps.HELLO_WORLD_JS, update=False)

    def test_008_create_project_named_123(self):
        """Create app starting with digits should not be possible without --force option"""
        result = Tns.create(app_name=Settings.AppName.WITH_NUMBER, template=Template.HELLO_WORLD_JS.local_package,
                            app_data=Apps.HELLO_WORLD_JS, update=False, verify=False)
        assert 'The project name does not start with letter and will fail to build for Android.' in result.output
        assert 'If You want to create project with this name add --force to the create command.' in result.output

        Tns.create(app_name=Settings.AppName.WITH_NUMBER, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=Apps.HELLO_WORLD_JS, force=True, update=False)

    def test_009_create_project_with_appid(self):
        """Create project with --appid option"""
        Tns.create(app_name=Settings.AppName.DEFAULT, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=Apps.HELLO_WORLD_JS, update=False, app_id='org.nativescript.MyApp')

    def test_010_create_project_with_named_app(self):
        """Create app named 'app' should not be possible without --force option"""
        Tns.create(app_name=Settings.AppName.APP_NAME, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=Apps.HELLO_WORLD_JS, force=True, update=False)
        json = App.get_package_json(app_name=Settings.AppName.APP_NAME)
        assert json['nativescript']['id'] == 'org.nativescript.{0}'.format(Settings.AppName.APP_NAME)

        # Create project should fail without --force
        result = Tns.create(app_name=Settings.AppName.APP_NAME, verify=False, update=False)
        assert "You cannot build applications named '" + self.app_name_app + "' in Xcode." in result.output

    def test_011_create_app_default(self):
        Folder.cleanup(os.path.join(Settings.AppName.APP_NAME))
        Tns.create(app_name=Settings.AppName.DEFAULT, default=True, update=False)

    def test_012_create_app_remove_app_resources(self):
        # creates valid project from local directory template
        Folder.clean(os.path.join("template-hello-world"))
        Folder.clean(os.path.join(Settings.AppName.DEFAULT))
        Git.clone(repo_url='git@github.com:NativeScript/template-hello-world.git',
                  local_folder="template-hello-world")
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME,  'template-hello-world', 'app', 'App_Resources'))
        file_path = os.path.join(Settings.TEST_RUN_HOME, 'template-hello-world', 'package.json')
        File.replace(file_path=file_path, old_string="tns-template-hello-world",
                     new_string="test-tns-template-hello-world")
        path = os.path.join(Settings.TEST_RUN_HOME, 'template-hello-world')
        Tns.create(app_name=Settings.AppName.DEFAULT, template=path)

    def test_013_create_app_scoped_packages(self):
        result = Tns.create(app_name=Settings.AppName.DEFAULT, template="@angular/core", verify=False)
        assert "Command npm install" not in result.output

    @parameterized.expand([
        "tns-template-hello-world",
        "https://github.com/NativeScript/template-hello-world.git",
        "https://github.com/NativeScript/template-hello-world-ts/tarball/master",
        "https://github.com/NativeScript/template-hello-world-ts.git#master",
        "https://github.com/NativeScript/template-hello-world-ng.git#master",
        "typescript",
        "tsc",
        "ng",
        "angular",
        "default",
        # "default@4.0.0"
    ])
    def test_014_create_project_with_template(self, template_source):
        """Create app should be possible with --template and npm packages, git repos and aliases"""
        Tns.create(app_name=Settings.AppName.DEFAULT, template=template_source, update=False)

    def test_015_create_project_with_local_directory_template(self):
        """--template should install all packages from package.json"""
        template_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'myCustomTemplate')
        Tns.create(app_name=Settings.AppName.DEFAULT, template=template_path, update=False)
        assert not Folder.is_empty(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'lodash'))
        assert not Folder.is_empty(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'minimist'))
        assert not Folder.is_empty(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'tns-core-modules'))
        assert not Folder.is_empty(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'tns-core-modules-widgets'))

    def test_016_create_project_with_no_app_resoruces(self):
        """--template should not create project if value is no npm installable"""
        Tns.create(app_name=Settings.AppName.DEFAULT, template="tns-template-hello-world-ts@2.0.0", update=False,
                   verify=False)
        res_path = os.path.join(Settings.AppName.DEFAULT, 'app', 'App_Resources')
        assert File.exists(res_path), "App Resouces not added by {N} CLI if missing in template"

    def test_017_create_project_with_wrong_template_path(self):
        """--template should not create project if value is no npm installable"""
        result = Tns.create(app_name=Settings.AppName.DEFAULT, template="invalidEntry", update=False, verify=False)
        assert "successfully created" not in result.output
        assert "Not Found" in result.output
        assert "404" in result.output

    def test_018_create_project_with_empty_template_path(self):
        result = Tns.create(app_name=Settings.AppName.DEFAULT, template="invalidEntry", update=False, verify=False)
        assert "successfully created" not in result.output
        assert "requires non-empty value" in result.output

    @staticmethod
    def __clean_folders():
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, 'folder'))
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, Settings.AppName.WITH_SPACE))
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, Settings.AppName.WITH_DASH))
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, Settings.AppName.WITH_NUMBER))
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, Settings.AppName.APP_NAME))
        Folder.clean(os.path.join("template-hello-world"))
