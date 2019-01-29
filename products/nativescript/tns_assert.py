import os

from core.enums.app_type import AppType
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.file_utils import Folder
from core.utils.json_utils import JsonUtils
from core.utils.perf_utils import PerfUtils
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
            app = app_name.rsplit('/')[-1]
            assert 'Now you can navigate to your project with $ cd' in output
            assert 'After that you can preview it on device by executing $ tns preview' in output
            assert 'After that you can run it on device/emulator by executing $ tns run <platform>' not in output
            assert 'Project {0} was successfully created'.format(app) in output, 'Failed to create {0}'.format(app)

        # Verify modules installed
        node_path = TnsPaths.get_app_node_modules_path(app_name=app_name, path=path)
        assert Folder.exists(os.path.join(node_path, 'tns-core-modules')), '{N} theme do not exists in app.'
        assert File.exists(os.path.join(node_path, 'tns-core-modules', 'tns-core-modules.d.ts'))

        # Verify {N} core theme is installed
        if theme:
            assert Folder.exists(os.path.join(node_path, 'nativescript-theme-core')), '{N} theme do not exists.'

        # Verify webpack is installed
        before_watch_hooks = os.path.join(app_path, 'hooks', 'before-watch')
        if webpack:
            assert Folder.exists(os.path.join(node_path, 'nativescript-dev-webpack')), 'Webpack not installed in app.'
            assert File.exists(os.path.join(app_path, 'webpack.config.js')), 'Missing webpack config.'
            assert File.exists(os.path.join(before_watch_hooks, 'nativescript-dev-webpack.js')), 'Hooks not installed.'

        # Assert app data
        if app_data is not None:
            # Verify typescript in TS and NG apps:
            if app_data.app_type in {AppType.TS, AppType.NG, AppType.SHARED_NG}:
                assert Folder.exists(os.path.join(node_path, 'nativescript-dev-typescript')), 'TS not installed in app.'
                assert File.exists(os.path.join(app_path, 'tsconfig.json')), 'Missing config.'
                if webpack:
                    assert File.exists(os.path.join(app_path, 'tsconfig.tns.json')), 'Missing config.'
                assert File.exists(os.path.join(before_watch_hooks, 'nativescript-dev-typescript.js')), \
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
    def platform_added(app_name, platform, output):
        platform_string = str(platform)
        # Verify output
        assert 'Platform {0} successfully added'.format(platform_string) in output
        # Verify package.json
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        package_json = os.path.join(app_path, 'package.json')
        json = JsonUtils.read(package_json)
        # noinspection SpellCheckingInspection
        assert json['nativescript']['tns-' + platform_string]['version'] is not None, \
            'tns-' + platform_string + ' not available in package.json of the app.'

    # noinspection PyUnusedLocal
    @staticmethod
    def build(app_name, platform=None, release=False, provision=Settings.IOS.DEV_PROVISION, for_device=False,
              bundle=False, aot=False, uglify=False, snapshot=False, log_trace=False, output=None, app_data=None):
        # pylint: disable=unused-argument
        # TODO: Implement it!

        # Verify output and exit code
        assert 'Project successfully built.' in output

        # Assert app data
        if app_data is not None:
            # Assert app type
            if app_data.app_type is AppType.JS:
                pass
            elif app_data.app_type is AppType.TS:
                pass
            elif app_data.app_type is AppType.NG:
                pass
            elif app_data.app_type is AppType.SHARED_NG:
                pass

            # Assert size
            if app_data.size is not None:
                pass
