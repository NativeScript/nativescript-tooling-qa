import os
import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder, File
from core.utils.npm import Npm
from data.sync.master_detail_vue import sync_master_detail_vue
from data.templates import Template
from products.nativescript.tns import Tns


class VueJSMasterDetailTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()

        # Ensure template package
        template_folder = os.path.join(Settings.TEST_SUT_HOME, 'templates', 'packages', Template.MASTER_DETAIL_VUE.name)
        out_file = os.path.join(Settings.TEST_SUT_HOME, Template.MASTER_DETAIL_VUE.name + '.tgz')
        Npm.pack(folder=template_folder, output_file=out_file)
        assert File.exists(out_file), "Failed to pack template: " + Template.MASTER_DETAIL_VUE.name

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.MASTER_DETAIL_VUE.local_package, update=True)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsRunTest.setUp(self)
        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        source_src = os.path.join(self.target_project_dir, 'app')
        target_src = os.path.join(self.source_project_dir, 'app')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)

    def test_100_run_android_bundle(self):
        sync_master_detail_vue(self.app_name, Platform.ANDROID, self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_100_run_ios_bundle(self):
        sync_master_detail_vue(self.app_name, Platform.IOS, self.sim)
