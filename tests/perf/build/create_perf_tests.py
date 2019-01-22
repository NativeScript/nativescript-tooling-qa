# pylint: disable=unused-argument
# pylint: disable=undefined-variable

import os

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.json_utils import JsonUtils
from core.utils.npm import Npm
from core.utils.perf_utils import PerfUtils
from data.templates import Template
from products.nativescript.tns import Tns

RETRY_COUNT = 3
TOLERANCE = 0.20
APP_NAME = Settings.AppName.DEFAULT
EXPECTED_RESULTS = JsonUtils.read(os.path.join(Settings.TEST_RUN_HOME, 'tests', 'perf', 'data.json'))


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
            lambda: Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=False),
            retry_count=RETRY_COUNT)
        expected = EXPECTED_RESULTS['hello-world-js']['create']
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'JS Hello Word project create time is not OK.'

    def test_002_create_ng_app(self):
        actual = PerfUtils.get_average_time(
            lambda: Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_NG.local_package, update=False),
            retry_count=RETRY_COUNT)
        expected = EXPECTED_RESULTS['hello-world-ng']['create']
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'NG Hello Word project create time is not OK.'

    def test_010_create_master_detail_app(self):
        actual = PerfUtils.get_average_time(
            lambda: Tns.create(app_name=APP_NAME,
                               template=Template.MASTER_DETAIL_NG.local_package,
                               update=False),
            retry_count=RETRY_COUNT)
        expected = EXPECTED_RESULTS['master-detail-ng']['create']
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'MasterDetailNG project create time is not OK.'
