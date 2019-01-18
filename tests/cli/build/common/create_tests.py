import os

from core.base_test.tns_test import TnsTest
from core.enums.app_type import AppType
from data.apps import Apps
from core.settings import Settings
from data.templates import Template
from products.nativescript.tns import Tns


class CreateTests(TnsTest):
    app_name_dash = "tns-app"
    app_name_space = "TNS App"
    app_name_123 = "123"
    app_name_app = "app"
    app_data_JS = Apps.HELLO_WORLD_JS
    app_data_TS = Apps.HELLO_WORLD_TS
    app_data_NG = Apps.HELLO_WORLD_NG

    js_app = Settings.AppName.DEFAULT + 'JS'
    js_source_project_dir = os.path.join(Settings.TEST_RUN_HOME, js_app)
    js_target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', js_app)

    ts_app = Settings.AppName.DEFAULT + 'TS'

    ng_app = Settings.AppName.DEFAULT + 'NG'
    ng_source_project_dir = os.path.join(Settings.TEST_RUN_HOME, ng_app)
    ng_target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', ng_app)

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_001_create_app_like_real_user(self):
        Tns.create(app_name=self.js_app, app_data=None)

    def test_002_create_apps(self):
        Tns.create(app_name=self.js_app, template=Template.HELLO_WORLD_JS.local_package, app_data=self.app_data_JS)
        Tns.create(app_name=self.ts_app, template=Template.HELLO_WORLD_TS.local_package, app_data=self.app_data_TS)
        Tns.create(app_name=self.ng_app, template=Template.HELLO_WORLD_NG.local_package, app_data=self.app_data_NG)
