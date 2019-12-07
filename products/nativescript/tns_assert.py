import os

from core.enums.app_type import AppType
from core.enums.framework_type import FrameworkType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.file_utils import Folder
from core.utils.json_utils import JsonUtils
from core.utils.perf_utils import PerfUtils
from core.utils.wait import Wait
from core.utils.run import run
from products.nativescript.app import App
from products.nativescript.tns_paths import TnsPaths


class TnsAssert(object):

    @staticmethod
    def created(app_name, output=None, app_data=None, path=Settings.TEST_RUN_HOME, webpack=True, theme=True):
        """
        Verify app is created properly.
        :param app_name: Name of the app.
        :param output: Console output of `tns create` command.
        :param app_data: AppInfo object.
        :param path: Base path where app is created.
        :param webpack: If true it will verify webpack plugin is installed.
        :param theme: If true it will verify default {N} theme is installed.
        """
        # Assert app exists
        app_path = os.path.join(path, app_name)
        assert Folder.exists(app_path), 'Failed to create app. ' + os.linesep + app_path + ' do not exists!'

        # Assert output
        if output is not None:
            assert 'Error:' not in output
            assert 'Now you can navigate to your project with $ cd' in output
            assert 'After that you can preview it on device by executing $ tns preview' in output
            assert 'After that you can run it on device/emulator by executing $ tns run <platform>' not in output
            assert 'Project {0} was successfully created'.format(app_name) in output, \
                'Failed to create {0}'.format(app_name)

        # Verify modules installed
        node_path = TnsPaths.get_app_node_modules_path(app_name=app_name, path=path)
        assert Folder.exists(os.path.join(node_path, 'tns-core-modules')), '{N} core modules not installed.'
        assert File.exists(os.path.join(node_path, 'tns-core-modules', 'tns-core-modules.d.ts'))

        # Verify {N} core theme is installed
        if theme:
            assert Folder.exists(os.path.join(node_path, '@nativescript', 'theme')), '{N} theme do not exists.'

        # Verify webpack is installed
        before_watch_hooks = os.path.join(app_path, 'hooks', 'before-watch')
        if webpack:
            assert Folder.exists(os.path.join(node_path, 'nativescript-dev-webpack')), 'Webpack not installed in app.'
            assert File.exists(os.path.join(app_path, 'webpack.config.js')), 'Missing webpack config.'

        # Assert app data
        if app_data is not None:
            # Verify typescript in TS and NG apps:
            if app_data.app_type in {AppType.TS, AppType.NG, AppType.SHARED_NG}:
                assert not Folder.exists(os.path.join(node_path, 'nativescript-dev-typescript')), \
                    'TS not installed in app.'
                assert File.exists(os.path.join(app_path, 'tsconfig.json')), 'Missing config.'
                if webpack:
                    assert File.exists(os.path.join(app_path, 'tsconfig.tns.json')), 'Missing config.'
                assert not File.exists(os.path.join(before_watch_hooks, 'nativescript-dev-typescript.js')), \
                    'Hooks not installed.'

            # Assert app id
            if app_data.bundle_id is not None:
                pass

            # Assert size
            if app_data.size is not None:
                app_size = Folder.get_size(app_path)
                assert PerfUtils.is_value_in_range(actual=app_size, expected=app_data.size.init,
                                                   tolerance=0.25), 'Actual project size is not expected!'

    @staticmethod
    def platform_added(app_name, platform, output, version=None):
        platform_string = str(platform)
        # Verify output
        assert 'Platform {0} successfully added'.format(platform_string) in output
        # Verify platform folder
        if platform == Platform.ANDROID:
            assert Folder.exists(TnsPaths.get_platforms_android_folder(app_name))
        else:
            assert Folder.exists(TnsPaths.get_platforms_ios_folder(app_name))
        # Verify package.json
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        package_json = os.path.join(app_path, 'package.json')
        json = JsonUtils.read(package_json)
        if version is not None:
            if 'next' or 'rc' in version:
                assert json['nativescript']['tns-' + platform_string]['version'] is not None
            else:
                assert version in json['nativescript']['tns-' + platform_string]['version']
        else:
            assert json['nativescript']['tns-' + platform_string]['version'] is not None, \
                'tns-' + platform_string + ' not available in package.json of the app.'

    @staticmethod
    def platform_list_status(output=None, prepared=Platform.NONE, added=Platform.NONE):
        """
        Assert platform list status
        :param output: Outout of `tns platform list` command
        :param prepared: Prepared platform.
        :param added: Added platform.
        """
        if output is not None:
            # Assert prepare status
            if prepared is Platform.NONE:
                if added is Platform.NONE:
                    assert 'The project is not prepared for' not in output
                else:
                    assert 'The project is not prepared for any platform' in output
            if prepared is Platform.ANDROID:
                assert 'The project is prepared for:  Android' in output
            if prepared is Platform.IOS:
                assert 'The project is prepared for:  iOS' in output
            if prepared is Platform.BOTH:
                assert 'The project is prepared for:  iOS and Android' in output

            # Assert platform added status
            if added is Platform.NONE:
                assert 'No installed platforms found. Use $ tns platform add' in output
                if Settings.HOST_OS is OSType.OSX:
                    assert 'Available platforms for this OS:  iOS and Android' in output
                else:
                    assert 'Available platforms for this OS:  Android' in output
            if added is Platform.ANDROID:
                assert 'Installed platforms:  android' in output
            if added is Platform.IOS:
                assert 'Installed platforms:  ios' in output
            if added is Platform.BOTH:
                assert 'Installed platforms:  android and ios' in output

    @staticmethod
    def platform_removed(app_name, platform, output):
        platform_string = str(platform)
        # Verify output
        assert 'Platform {0} successfully removed'.format(platform_string) in output
        # Verify package.json
        app_path = TnsPaths.get_app_path(app_name)
        package_json = os.path.join(app_path, 'package.json')
        json = JsonUtils.read(package_json)
        assert not 'tns-' + platform_string in json
        if platform == Platform.ANDROID:
            assert not Folder.exists(TnsPaths.get_platforms_android_folder(app_name))
        else:
            assert not Folder.exists(TnsPaths.get_platforms_ios_folder(app_name))

    @staticmethod
    def test_initialized(app_name, framework, output):
        """
        Execute `tns test init` command.
        :param app_name: App name (passed as --path <App name>)
        :param framework: FrameworkType enum value.
        :param output: Output of `tns test init` command.
        :return: Result of `tns test init` command.
        """
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        config = os.path.join(app_path, 'karma.conf.js')
        assert App.is_dependency(app_name=app_name, dependency='nativescript-unit-test-runner')
        if framework == FrameworkType.JASMINE:
            assert "frameworks: ['jasmine']" in File.read(config), 'Framework not set in config file.'
            assert App.is_dev_dependency(app_name=app_name, dependency='karma-jasmine')
        if framework == FrameworkType.MOCHA:
            assert "frameworks: ['mocha', 'chai']" in File.read(config), 'Frameworks not set in config file.'
            assert App.is_dev_dependency(app_name=app_name, dependency='karma-mocha')
            assert App.is_dev_dependency(app_name=app_name, dependency='karma-chai')
        if framework == FrameworkType.QUNIT:
            assert "frameworks: ['qunit']" in File.read(config), 'Framework not set in config file.'
            assert App.is_dev_dependency(app_name=app_name, dependency='karma-qunit')
        if output is not None:
            assert 'Successfully installed plugin nativescript-unit-test-runner' in output
            assert 'Example test file created in' in output
            assert 'Run your tests using the' in output

    @staticmethod
    def file_is_synced_once(log, device, file_name):
        """
        Assert file is synced once on livesync.
        :param log: log or part of log you want to check
        :param platform: The platform you are syncing on.
        :param file_name: name of the file you are syncing.
        """
        assert log.count('Start syncing changes for device {0}'.format(str(device.model))) == 1, \
            "File is synced more than once!"
        # assert log.count('hot-update.json for device') == 1, "File is synced more than once!"
        assert file_name in log

    @staticmethod
    def snapshot_skipped(snapshot, result, release):
        """
        Verify if snapshot flag is passed it it skipped.
        :param snapshot: True if snapshot flag is present.
        :param result: Result of `tns run` command.
        :param release: True if release build
        """
        if snapshot and Settings.HOST_OS == OSType.WINDOWS or snapshot and not release:
            msg = 'Bear in mind that snapshot is only available in release builds and is NOT available on Windows'
            skip_snapshot = Wait.until(lambda: 'Stripping the snapshot flag' in File.read(result.log_file), timeout=180)
            assert skip_snapshot, 'Not message that snapshot is skipped.'
            assert msg in File.read(result.log_file), 'No message that snapshot is NOT available on Windows.'

    @staticmethod
    def snapshot_build(path_to_apk, path_to_extract_apk):
        """
        Verify snapshot build.
        :param path_to_apk: path to the built apk.
        :param path_to_extract_apk: path where to extract the .apk files
        """
        # Extract the built .apk file
        File.unzip(path_to_apk, path_to_extract_apk)
        # Verify lib files
        assert File.exists(os.path.join(path_to_extract_apk, 'lib', 'x86', 'libNativeScript.so'))
        assert File.exists(os.path.join(path_to_extract_apk, 'lib', 'x86_64', 'libNativeScript.so'))
        assert File.exists(os.path.join(path_to_extract_apk, 'lib', 'arm64-v8a', 'libNativeScript.so'))
        assert File.exists(os.path.join(path_to_extract_apk, 'lib', 'armeabi-v7a', 'libNativeScript.so'))
        # Verify snapshot files
        assert File.exists(os.path.join(path_to_extract_apk, 'assets', 'snapshots', 'x86', 'snapshot.blob'))
        assert File.exists(os.path.join(path_to_extract_apk, 'assets', 'snapshots', 'x86_64', 'snapshot.blob'))
        assert File.exists(os.path.join(path_to_extract_apk, 'assets', 'snapshots', 'arm64-v8a', 'snapshot.blob'))
        assert File.exists(os.path.join(path_to_extract_apk, 'assets', 'snapshots', 'armeabi-v7a', 'snapshot.blob'))

    @staticmethod
    def string_in_android_manifest(path_to_apk, string):
        """
        Verify string exists in AndroidManifest.xml file in the built .apk
        :param path_to_apk: path to the built apk.
        :param string: string you want to assert exists in AndroidManifest.xml
        """
        apkanalyzer = os.path.join(os.environ.get('ANDROID_HOME'), 'tools', 'bin', 'apkanalyzer')
        command = '{0} manifest print "{1}"'.format(apkanalyzer, path_to_apk)
        if Settings.HOST_OS == OSType.WINDOWS:
            apk_tool = os.path.join(os.environ.get('APKTOOL'), 'apktool.jar')
            command = '{0} d {1} -f -o {2}'.format(apk_tool, path_to_apk, Settings.TEST_OUT_TEMP)
        result = run(command, timeout=30)
        if Settings.HOST_OS == OSType.WINDOWS:
            manifest = File.read(os.path.join(Settings.TEST_OUT_TEMP, 'AndroidManifest.xml'))
            assert string in manifest, '{0} NOT found in AndroidManifest.xml'.format(string)
        else:
            assert string in result.output, '{0} NOT found in AndroidManifest.xml'.format(string)
        Log.info('{0} found in AndroidManifest.xml'.format(string))
