import os

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.file_utils import Folder
from core.utils.git import Git
from core.utils.json_utils import JsonUtils
from core.utils.npm import Npm
from core.utils.perf_utils import PerfUtils
from data.templates import Template
from products.nativescript.tns import Tns

retry_count = 3
tolerance = 0.20
app_name = Settings.AppName.DEFAULT
expected_results = JsonUtils.read(os.path.join(Settings.TEST_RUN_HOME, 'tests', 'perf', 'data.json'))


# noinspection PyMethodMayBeStatic
class CreateAppPerfTests(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)
        Npm.cache_clean()

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_001_create_js_app(self):
        actual = PerfUtils.get_average_time(
            lambda: Tns.create(app_name=app_name, template=Template.HELLO_WORLD_JS.local_package, update=False),
            retry_count=retry_count)
        expected = expected_results['hello-world-js']['create']
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'JS Hello Word project create time is not OK.'

    def test_002_create_ng_app(self):
        actual = PerfUtils.get_average_time(
            lambda: Tns.create(app_name=app_name, template=Template.HELLO_WORLD_NG.local_package, update=False),
            retry_count=retry_count)
        expected = expected_results['hello-world-ng']['create']
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'NG Hello Word project create time is not OK.'

    def test_010_create_master_detail_app(self):
        local_folder = os.path.join(Settings.TEST_SUT_HOME, Template.MASTER_DETAIL_NG.name)
        local_package = os.path.join(Settings.TEST_SUT_HOME, Template.MASTER_DETAIL_NG.name + '.tgz')
        Folder.clean(local_folder)
        Git.clone(repo_url=Template.MASTER_DETAIL_NG.repo, local_folder=local_folder)
        Npm.pack(folder=local_folder, output_file=local_package)
        Folder.clean(local_folder)
        actual = PerfUtils.get_average_time(lambda: Tns.create(app_name=app_name, template=local_package, update=False),
                                            retry_count=retry_count)
        expected = expected_results['master-detail-ng']['create']
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'MasterDetailNG project create time is not OK.'
