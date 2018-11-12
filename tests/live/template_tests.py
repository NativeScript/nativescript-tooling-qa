import json
import os

from nose_parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder
from data.templates import Template
from products.nativescript.app import App
from products.nativescript.tns import Tns


# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class TemplateTests(TnsTest):
    # IF env. variable UPDATE=False is set then apps will be not updated (test as is).
    update = json.loads(os.environ.get('UPDATE', 'True').lower())

    app_name = Settings.AppName.DEFAULT
    app_folder = os.path.join(Settings.TEST_RUN_HOME, app_name)
    emu = None
    sim = None

    test_data = [
        [Template.HELLO_WORLD_JS.name, Template.HELLO_WORLD_JS],
        [Template.HELLO_WORLD_TS.name, Template.HELLO_WORLD_TS],
        [Template.HELLO_WORLD_NG.name, Template.HELLO_WORLD_NG],
        [Template.BLANK_JS.name, Template.BLANK_JS],
        [Template.BLANK_TS.name, Template.BLANK_TS],
        [Template.BLANK_NG.name, Template.BLANK_NG],
        [Template.DRAWER_NAVIGATION_JS.name, Template.DRAWER_NAVIGATION_JS],
        [Template.DRAWER_NAVIGATION_TS.name, Template.DRAWER_NAVIGATION_TS],
        [Template.DRAWER_NAVIGATION_NG.name, Template.DRAWER_NAVIGATION_NG],
        [Template.TAB_NAVIGATION_JS.name, Template.TAB_NAVIGATION_JS],
        [Template.TAB_NAVIGATION_TS.name, Template.TAB_NAVIGATION_TS],
        [Template.TAB_NAVIGATION_NG.name, Template.TAB_NAVIGATION_NG],
        [Template.MASTER_DETAIL_JS.name, Template.MASTER_DETAIL_JS],
        [Template.MASTER_DETAIL_TS.name, Template.MASTER_DETAIL_TS],
        [Template.MASTER_DETAIL_NG.name, Template.MASTER_DETAIL_NG],
        [Template.MASTER_DETAIL_KINVEY_JS.name, Template.MASTER_DETAIL_KINVEY_JS],
        [Template.MASTER_DETAIL_KINVEY_TS.name, Template.MASTER_DETAIL_KINVEY_TS],
        [Template.MASTER_DETAIL_KINVEY_NG.name, Template.MASTER_DETAIL_KINVEY_NG],
        [Template.ENTERPRISE_AUTH_JS.name, Template.ENTERPRISE_AUTH_JS],
        [Template.ENTERPRISE_AUTH_TS.name, Template.ENTERPRISE_AUTH_TS],
        [Template.ENTERPRISE_AUTH_NG.name, Template.ENTERPRISE_AUTH_NG],
        [Template.HEALTH_SURVEY_NG.name, Template.HEALTH_SURVEY_NG],
        [Template.PATIENT_CARE_NG.name, Template.PATIENT_CARE_NG],
        [Template.VUE_BLANK.name, Template.VUE_BLANK],
        [Template.VUE_MASTER_DETAIL.name, Template.VUE_MASTER_DETAIL]
    ]

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

    def setUp(self):
        TnsTest.setUp(self)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    @parameterized.expand(test_data)
    def test(self, template_name, template_info):
        # Create app
        app_name = template_info.name.replace('template-', '')
        local_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        Tns.create(app_name=app_name, template=template_info.repo, update=self.update)
        App.ensure_webpack_installed(app_name=app_name)

        # Build in release
        Tns.build_android(app_name=app_name, release=True, bundle=True, aot=True, uglify=True, snapshot=True)
        if Settings.HOST_OS is OSType.OSX:
            Tns.build_ios(app_name=app_name, release=True, for_device=True, bundle=True, aot=True, uglify=True)

        # Run with bundle
        Tns.run_android(app_name=app_name, device=self.emu.id, bundle=True, justlaunch=True, wait=True)
        assert self.emu.wait_for_text(texts=template_info.texts, timeout=120), \
            '{0} does not look OK on {1}.'.format(app_name, self.emu.name)
        if Settings.HOST_OS is OSType.OSX:
            Tns.run_ios(app_name=app_name, device=self.sim.id, bundle=True, justlaunch=True, wait=True)
            assert self.sim.wait_for_text(texts=template_info.texts, timeout=120), \
                '{0} does not look OK on {1}.'.format(app_name, self.sim.name)

        # Cleanup
        Folder.clean(local_path)
