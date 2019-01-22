import os

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.file_utils import Folder
from data.apps import Apps
from data.templates import Template
from products.nativescript.tns import Tns


class CreateTests(TnsTest):
    app_data_JS = Apps.HELLO_WORLD_JS
    app_data_TS = Apps.HELLO_WORLD_TS
    app_data_NG = Apps.HELLO_WORLD_NG

    js_app = Settings.AppName.DEFAULT + 'JS'
    ts_app = Settings.AppName.DEFAULT + 'TS'
    ng_app = Settings.AppName.DEFAULT + 'NG'

    js_app_space = Settings.AppName.WITH_SPACE
    js_app_dash = Settings.AppName.WITH_DASH
    js_app_number = Settings.AppName.WITH_NUMBER

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, 'folder'))
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, 'js_app_space'))
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, 'js_app_dash'))
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, 'js_app_number'))

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_001_create_app_like_real_user(self):
        Tns.create(app_name=self.js_app, app_data=None)

    def test_002_create_app_template_js(self):
        """Create app with --template js project without update modules"""
        Tns.create(app_name=self.js_app, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=self.app_data_JS, update=False, verify=False)

    def test_003_create_app_template_ts(self):
        """Create app with --template ts project without update modules"""
        Tns.create(app_name=self.ts_app, template=Template.HELLO_WORLD_TS.local_package,
                   app_data=self.app_data_TS, update=False, verify=False)

    def test_004_create_app_template_ng(self):
        """Create app with --template ng project without update modules"""
        Tns.create(app_name=self.ng_app, template=Template.HELLO_WORLD_NG.local_package,
                   app_data=self.app_data_NG, update=False, verify=False)

    def test_005_create_project_with_path(self):
        """Create project with --path option"""
        Tns.create(app_name=self.js_app, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=self.app_data_JS, path=os.path.join(Settings.TEST_RUN_HOME, 'folder', 'subfolder'),
                   update=False, verify=False)
        assert Folder.exists(os.path.join(Settings.TEST_RUN_HOME, 'folder', 'subfolder', 'TestAppJS'))

    def test_006_create_project_with_space(self):
        """ Create project with space is possible, but packageId will skip the space symbol"""
        Tns.create(app_name=self.js_app_space, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=self.app_data_JS, update=False, verify=False)

    def test_007_create_project_with_space(self):
        """ Create project with dash is possible, but packageId will skip the dash symbol"""
        Tns.create(app_name=self.js_app_dash, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=self.app_data_JS, update=False, verify=False)

    def test_008_create_project_named_123(self):
        """Create app starting with digits should not be possible without --force option"""
        Tns.create(app_name=self.js_app_number, template=Template.HELLO_WORLD_JS.local_package,
                   app_data=self.app_data_JS, update=False, verify=False)
        # TODO: package_json contains

    def test_009_create_project_with_appid(self):
        """Create project with --appid option"""
        Tns.create(app_name=self.js_app, template=Template.HELLO_WORLD_JS.local_package, app_data=self.app_data_JS,
                   update=False, verify=False, app_id='org.nativescript.MyApp')
