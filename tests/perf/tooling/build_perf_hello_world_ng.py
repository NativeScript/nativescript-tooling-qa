# pylint: disable=unused-argument
# pylint: disable=undefined-variable

import json
import os
import unittest

from parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder, File
from core.utils.gradle import Gradle
from core.utils.json_utils import JsonUtils
from core.utils.npm import Npm
from core.utils.perf_utils import PerfUtils
from core.utils.xcode import Xcode
from data.changes import Changes, Sync
from data.templates import Template
from products.nativescript.tns import Tns

RETRY_COUNT = 3
TOLERANCE = 0.20
APP_NAME = Settings.AppName.DEFAULT
EXPECTED_RESULTS = JsonUtils.read(os.path.join(Settings.TEST_RUN_HOME, 'tests', 'perf', 'data.json'))


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class PrepareAndBuildPerfTests(TnsTest):
    TEST_DATA = [
        ('hello-world-ng', Template.HELLO_WORLD_NG.local_package, Changes.NGHelloWorld.TS)
    ]

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    @parameterized.expand(TEST_DATA)
    def test_001_prepare_data(self, template, template_package, change_set):
        android_result_file = Helpers.get_result_file_name(template, Platform.ANDROID)
        ios_result_file = Helpers.get_result_file_name(template, Platform.IOS)
        Helpers.prepare_and_build(template=template_package, platform=Platform.ANDROID,
                                  change_set=change_set, result_file=android_result_file)
        Helpers.prepare_and_build(template=template_package, platform=Platform.IOS,
                                  change_set=change_set, result_file=ios_result_file)

    @parameterized.expand(TEST_DATA)
    def test_200_prepare_android_initial(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, 'prepare_initial')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, 'prepare_initial')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Initial android prepare time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_201_prepare_ios_initial(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.IOS, 'prepare_initial')
        expected = Helpers.get_expected_result(template, Platform.IOS, 'prepare_initial')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Initial ios prepare time is not OK.'

    @parameterized.expand(TEST_DATA)
    def test_300_build_android_initial(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, 'build_initial')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, 'build_initial')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Initial android build time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_301_build_ios_initial(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.IOS, 'build_initial')
        expected = Helpers.get_expected_result(template, Platform.IOS, 'build_initial')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Initial ios build time is not OK.'

    @parameterized.expand(TEST_DATA)
    def test_310_build_android_incremental(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, 'build_incremental')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, 'build_incremental')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Incremental android build time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_311_build_ios_incremental(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.IOS, 'build_incremental')
        expected = Helpers.get_expected_result(template, Platform.IOS, 'build_incremental')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Incremental ios build time is not OK.'


class PrepareBuildInfo(object):
    prepare_initial = 0
    prepare_skip = 0
    prepare_incremental = 0
    build_initial = 0
    build_incremental = 0


class Helpers(object):
    @staticmethod
    def prepare_and_build(template, platform, change_set, result_file):
        prepare_initial = 0
        build_initial = 0
        build_incremental = 0
        for _ in range(RETRY_COUNT):
            Tns.kill()
            Gradle.kill()
            Npm.cache_clean()
            Xcode.cache_clean()
            Folder.clean(folder=os.path.join(Settings.TEST_RUN_HOME, APP_NAME))
            Tns.create(app_name=APP_NAME, template=template, update=True)
            if platform == Platform.ANDROID:
                Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)
            elif platform == Platform.IOS:
                Tns.platform_add_ios(app_name=APP_NAME, framework_path=Settings.IOS.FRAMEWORK_PATH)
            else:
                raise Exception('Unknown platform: ' + str(platform))

            # Prepare
            time = Tns.prepare(app_name=APP_NAME, platform=platform, bundle=True).duration
            prepare_initial = prepare_initial + time

            # Build
            time = Tns.build(app_name=APP_NAME, platform=platform, bundle=True).duration
            build_initial = build_initial + time
            Sync.replace(app_name=APP_NAME, change_set=change_set)
            time = Tns.build(app_name=APP_NAME, platform=platform, bundle=True).duration
            build_incremental = build_incremental + time

        # Calculate averages
        result = PrepareBuildInfo()
        result.prepare_initial = prepare_initial / RETRY_COUNT
        result.build_initial = build_initial / RETRY_COUNT
        result.build_incremental = build_incremental / RETRY_COUNT

        # Save to results file
        File.delete(path=result_file)
        result_json = json.dumps(result, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        File.write(path=result_file, text=str(result_json))

    @staticmethod
    def get_result_file_name(template, platform):
        result_file = os.path.join(Settings.TEST_OUT_HOME, '{0}_{1}.json'.format(template, str(platform)))
        return result_file

    @staticmethod
    def get_actual_result(template, platform, entry):
        result_file = Helpers.get_result_file_name(template, platform)
        return JsonUtils.read(result_file)[entry]

    @staticmethod
    def get_expected_result(template, platform, entry):
        platform = str(platform)
        return EXPECTED_RESULTS[template][platform][entry]
