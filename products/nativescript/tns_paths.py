# pylint: disable=unused-argument
# TODO: Implement it!
import os

from core.settings import Settings


# noinspection PyUnusedLocal


class TnsPaths(object):

    @staticmethod
    def get_app_path(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(path, app_name)

    @staticmethod
    def get_app_node_modules_path(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_app_path(app_name=app_name, path=path), 'node_modules')

    @staticmethod
    def get_path_app_resources(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_app_path(app_name=app_name, path=path), 'app', 'App_Resources')

    @staticmethod
    def get_path_app_resources_main_android(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_app_path(app_name=app_name, path=path), 'app', 'App_Resources',
                            'Android', 'src', 'main')

    @staticmethod
    def get_platforms_android_folder(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_app_path(app_name=app_name, path=path), 'platforms', 'android')

    @staticmethod
    def get_platforms_ios_folder(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_app_path(app_name=app_name, path=path), 'platforms', 'ios')

    @staticmethod
    def get_platforms_android_src_main_path(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_platforms_android_folder(app_name=app_name, path=path), 'app', 'src', 'main')

    @staticmethod
    def get_platforms_android_app_path(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_platforms_android_folder(app_name=app_name, path=path), 'app', 'src', 'main',
                            'assets', 'app')

    @staticmethod
    def get_platforms_ios_app_path(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_platforms_ios_folder(app_name=app_name, path=path), app_name, 'app')

    @staticmethod
    def get_platforms_android_npm_modules(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_platforms_android_folder(app_name=app_name, path=path), 'app', 'src', 'main',
                            'assets', 'app', 'tns_modules')

    @staticmethod
    def get_platforms_ios_npm_modules(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_platforms_ios_folder(app_name=app_name, path=path), app_name,
                            'app', 'tns_modules')

    @staticmethod
    def get_apk_path(app_name, release=False, path=Settings.TEST_RUN_HOME):
        build_path = os.path.join(TnsPaths.get_platforms_android_folder(app_name=app_name, path=path), 'app', 'build')
        if release:
            return os.path.join(build_path, 'outputs', 'apk', 'release', 'app-release.apk')
        else:
            return os.path.join(build_path, 'outputs', 'apk', 'debug', 'app-debug.apk')

    @staticmethod
    def get_ipa_path(app_name, for_device=False, release=False, path=Settings.TEST_RUN_HOME):
        app_name = TnsPaths.__get_trimmed_app_name(app_name=app_name)
        base_path = os.path.join(TnsPaths.get_platforms_ios_folder(app_name=app_name, path=path), 'build')
        if for_device:
            if release:
                return os.path.join(base_path, 'Release-iphoneos', '{0}.ipa'.format(app_name))
            else:
                return os.path.join(base_path, 'Debug-iphoneos', '{0}.ipa'.format(app_name))
        else:
            if release:
                return os.path.join(base_path, 'Release-iphonesimulator', '{0}.app'.format(app_name))
            else:
                return os.path.join(base_path, 'Debug-iphonesimulator', '{0}.app'.format(app_name))

    @staticmethod
    def get_app_ios_path(app_name, path=Settings.TEST_RUN_HOME):
        return ''

    @staticmethod
    def get_bundle_id(app_name):
        return 'org.nativescript.' + TnsPaths.__get_trimmed_app_name(app_name=app_name)

    @staticmethod
    def __get_trimmed_app_name(app_name):
        """
        Get app name in format for bundle id or native platforms.
        :param app_name: App name.
        :return: Formated app name.
        """
        if '-' in app_name:
            app_name = app_name.replace('-', '')
        if ' ' in app_name:
            app_name = app_name.replace(' ', '')
        if '"' in app_name:
            app_name = app_name.replace('"', '')
        return app_name
