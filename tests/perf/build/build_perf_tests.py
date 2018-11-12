import json
import os
import unittest

from parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder, File
from core.utils.git import Git
from core.utils.gradle import Gradle
from core.utils.json_utils import JsonUtils
from core.utils.npm import Npm
from core.utils.perf_utils import PerfUtils
from core.utils.xcode import Xcode
from data.changes import Changes, Sync
from data.templates import Template
from products.nativescript.tns import Tns

retry_count = 3
tolerance = 0.20
app_name = Settings.AppName.DEFAULT
expected_results = JsonUtils.read(os.path.join(Settings.TEST_RUN_HOME, 'tests', 'perf', 'data.json'))


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class PrepareAndBuildPerfTests(TnsTest):
    TEST_DATA = [
        ('hello-world-js', Template.HELLO_WORLD_JS.local_package, Changes.JSHelloWord.JS, False),
        ('hello-world-ng', Template.HELLO_WORLD_NG.local_package, Changes.NGHelloWorld.TS, False),
        ('master-detail-ng', Template.MASTER_DETAIL_NG.local_package, Changes.MasterDetailNG.TS, False),
        ('hello-world-js', Template.HELLO_WORLD_JS.local_package, Changes.JSHelloWord.JS, True),
        ('hello-world-ng', Template.HELLO_WORLD_NG.local_package, Changes.NGHelloWorld.TS, True),
        ('master-detail-ng', Template.MASTER_DETAIL_NG.local_package, Changes.MasterDetailNG.TS, True),
    ]

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

        # Get master detail template locally.
        local_folder = os.path.join(Settings.TEST_SUT_HOME, Template.MASTER_DETAIL_NG.name)
        local_package = os.path.join(Settings.TEST_SUT_HOME, Template.MASTER_DETAIL_NG.name + '.tgz')
        Folder.clean(local_folder)
        Git.clone(repo_url=Template.MASTER_DETAIL_NG.repo, local_folder=local_folder)
        Npm.pack(folder=local_folder, output_file=local_package)
        Folder.clean(local_folder)
        Template.MASTER_DETAIL_NG.local_package = local_package

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    @parameterized.expand(TEST_DATA)
    def test_001_prepare_data(self, template, template_package, change_set, bundle):
        android_result_file = Helpers.get_result_file_name(template, Platform.ANDROID, bundle)
        ios_result_file = Helpers.get_result_file_name(template, Platform.IOS, bundle)
        Helpers.prepare_and_build(template=template_package, platform=Platform.ANDROID, bundle=bundle,
                                  change_set=change_set, result_file=android_result_file)
        Helpers.prepare_and_build(template=template_package, platform=Platform.IOS, bundle=bundle,
                                  change_set=change_set, result_file=ios_result_file)

    @parameterized.expand(TEST_DATA)
    def test_200_prepare_android_initial(self, template, template_package, change_set, bundle):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, bundle, 'prepare_initial')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, bundle, 'prepare_initial')
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'Initial android prepare time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_201_prepare_ios_initial(self, template, template_package, change_set, bundle):
        actual = Helpers.get_actual_result(template, Platform.iOS, bundle, 'prepare_initial')
        expected = Helpers.get_expected_result(template, Platform.iOS, bundle, 'prepare_initial')
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'Initial ios prepare time is not OK.'

    @parameterized.expand(TEST_DATA)
    def test_210_prepare_android_skip(self, template, template_package, change_set, bundle):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, bundle, 'prepare_skip')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, bundle, 'prepare_skip')
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'Skip android prepare time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_211_prepare_ios_skip(self, template, template_package, change_set, bundle):
        actual = Helpers.get_actual_result(template, Platform.iOS, bundle, 'prepare_skip')
        expected = Helpers.get_expected_result(template, Platform.iOS, bundle, 'prepare_skip')
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'Skip ios prepare time is not OK.'

    @parameterized.expand(TEST_DATA)
    def test_220_prepare_android_incremental(self, template, template_package, change_set, bundle):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, bundle, 'prepare_incremental')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, bundle, 'prepare_incremental')
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'Incremental android prepare time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_221_prepare_ios_incremental(self, template, template_package, change_set, bundle):
        actual = Helpers.get_actual_result(template, Platform.iOS, bundle, 'prepare_incremental')
        expected = Helpers.get_expected_result(template, Platform.iOS, bundle, 'prepare_incremental')
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'Incremental ios prepare time is not OK.'

    @parameterized.expand(TEST_DATA)
    def test_300_build_android_initial(self, template, template_package, change_set, bundle):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, bundle, 'build_initial')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, bundle, 'build_initial')
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'Initial android build time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_301_build_ios_initial(self, template, template_package, change_set, bundle):
        actual = Helpers.get_actual_result(template, Platform.iOS, bundle, 'build_initial')
        expected = Helpers.get_expected_result(template, Platform.iOS, bundle, 'build_initial')
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'Initial ios build time is not OK.'

    @parameterized.expand(TEST_DATA)
    def test_310_build_android_incremental(self, template, template_package, change_set, bundle):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, bundle, 'build_incremental')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, bundle, 'build_incremental')
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'Incremental android build time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_311_build_ios_incremental(self, template, template_package, change_set, bundle):
        actual = Helpers.get_actual_result(template, Platform.iOS, bundle, 'build_incremental')
        expected = Helpers.get_expected_result(template, Platform.iOS, bundle, 'build_incremental')
        assert PerfUtils.is_value_in_range(actual, expected, tolerance), 'Incremental ios build time is not OK.'


class PrepareBuildInfo(object):
    prepare_initial = 0
    prepare_skip = 0
    prepare_incremental = 0
    build_initial = 0
    build_incremental = 0


class Helpers(object):
    @staticmethod
    def prepare_and_build(template, platform, bundle, change_set, result_file):
        prepare_initial = 0
        prepare_skip = 0
        prepare_incremental = 0
        build_initial = 0
        build_incremental = 0
        for i in range(retry_count):
            Tns.kill()
            Gradle.kill()
            Npm.cache_clean()
            Xcode.cache_clean()
            Folder.clean(folder=os.path.join(Settings.TEST_RUN_HOME, app_name))
            Tns.create(app_name=app_name, template=template, update=True)
            if platform == Platform.ANDROID:
                Tns.platform_add_android(app_name=app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
            elif platform == Platform.IOS:
                Tns.platform_add_ios(app_name=app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)
            else:
                raise Exception('Unknown platform: ' + str(platform))

            # Prepare
            time = Tns.prepare(app_name=app_name, platform=platform, bundle=bundle).duration
            prepare_initial = prepare_initial + time
            time = Tns.prepare(app_name=app_name, platform=platform, bundle=bundle).duration
            prepare_skip = prepare_skip + time
            Sync.replace(app_name=app_name, change_set=change_set)
            time = Tns.prepare(app_name=app_name, platform=platform, bundle=bundle).duration
            prepare_incremental = prepare_incremental + time

            # Build
            time = Tns.build(app_name=app_name, platform=platform, bundle=bundle).duration
            build_initial = build_initial + time
            Sync.revert(app_name=app_name, change_set=change_set)
            time = Tns.build(app_name=app_name, platform=platform, bundle=bundle).duration
            build_incremental = build_incremental + time

        # Calculate averages
        result = PrepareBuildInfo()
        result.prepare_initial = prepare_initial / retry_count
        result.prepare_skip = prepare_skip / retry_count
        result.prepare_incremental = prepare_incremental / retry_count
        result.build_initial = build_initial / retry_count
        result.build_incremental = build_incremental / retry_count

        # Save to results file
        File.clean(path=result_file)
        result_json = json.dumps(result, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        File.write(path=result_file, text=str(result_json))

    @staticmethod
    def get_result_file_name(template, platform, bundle):
        result_file = os.path.join(Settings.TEST_OUT_HOME, '{0}_{1}.json'.format(template, platform))
        if bundle:
            result_file = result_file.replace('.json', '_bundle.json')
        return result_file

    @staticmethod
    def get_actual_result(template, platform, bundle, entry):
        result_file = Helpers.get_result_file_name(template, platform, bundle)
        return JsonUtils.read(result_file)[entry]

    @staticmethod
    def get_expected_result(template, platform, bundle, entry):
        if bundle:
            platform = str(platform) + '_bundle'
        return expected_results[template][platform][entry]
