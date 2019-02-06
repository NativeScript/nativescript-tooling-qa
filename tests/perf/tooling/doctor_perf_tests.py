import os

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.perf_utils import PerfUtils
from data.templates import Template
from products.nativescript.tns import Tns

RETRY_COUNT = 3
APP_NAME = Settings.AppName.DEFAULT


# noinspection PyMethodMayBeStatic
class DoctorPerfTests(TnsTest):
    ANDROID_HOME = os.environ.get('ANDROID_HOME')
    JAVA_HOME = os.environ.get('JAVA_HOME')

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.platform_add_ios(app_name=APP_NAME, framework_path=Settings.IOS.FRAMEWORK_PATH)
        Tns.prepare_android(app_name=APP_NAME)
        Tns.prepare_ios(app_name=APP_NAME)

    def setUp(self):
        TnsTest.setUp(self)

    def test_300_doctor_performance_outside_project(self):
        time = PerfUtils.get_average_time(lambda: Tns.doctor(), retry_count=RETRY_COUNT)
        assert PerfUtils.is_value_in_range(actual=time, expected=7.67), 'Doctor exec time is not OK.'

    def test_301_doctor_performance_inside_project(self):
        time = PerfUtils.get_average_time(lambda: Tns.doctor(app_name=APP_NAME), retry_count=RETRY_COUNT)
        assert PerfUtils.is_value_in_range(actual=time, expected=9.85), 'Doctor exec time is not OK.'

    def test_302_prepare_with_doctor_do_not_make_it_much_slower(self):
        pa_d_time = PerfUtils.get_average_time(lambda: Tns.prepare_android(app_name=APP_NAME), retry_count=RETRY_COUNT)
        pi_d_time = PerfUtils.get_average_time(lambda: Tns.prepare_ios(app_name=APP_NAME), retry_count=RETRY_COUNT)

        os.environ['NS_SKIP_ENV_CHECK'] = 'true'
        pa_nd_time = PerfUtils.get_average_time(lambda: Tns.prepare_android(app_name=APP_NAME), retry_count=RETRY_COUNT)
        pi_nd_time = PerfUtils.get_average_time(lambda: Tns.prepare_ios(app_name=APP_NAME), retry_count=RETRY_COUNT)

        android_diff = pa_d_time - pa_nd_time
        ios_diff = pi_d_time - pi_nd_time
        assert PerfUtils.is_value_in_range(android_diff, 3, tolerance=1.0), 'Prepare android with common is slower.'
        assert PerfUtils.is_value_in_range(ios_diff, 6, tolerance=0.5), 'Prepare ios with common is slower.'
