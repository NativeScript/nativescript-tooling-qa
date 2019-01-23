import os

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.file_utils import Folder
from data.apps import Apps
from data.templates import Template
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
        """ Create project with space is possible, but packageId will skip the space symbol"""
        Tns.create(app_name=Settings.AppName.WITH_DASH, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=Apps.HELLO_WORLD_JS, update=False)

    def test_007_create_project_with_space(self):
        """ Create project with dash is possible, but packageId will skip the dash symbol"""
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

    @staticmethod
    def __clean_folders():
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, 'folder'))
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, Settings.AppName.WITH_SPACE))
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, Settings.AppName.WITH_DASH))
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, Settings.AppName.WITH_NUMBER))
