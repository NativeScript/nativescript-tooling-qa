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
    def get_platforms_android_folder(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_app_path(app_name=app_name, path=path), 'platforms', 'android')

    @staticmethod
    def get_platforms_ios_folder(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_app_path(app_name=app_name, path=path), 'platforms', 'ios')

    @staticmethod
    def get_platforms_android_npm_modules(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_platforms_android_folder(app_name=app_name, path=path), 'app', 'src', 'main',
                            'assets', 'app', 'tns_modules')

    @staticmethod
    def get_platforms_ios_npm_modules(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_platforms_ios_folder(app_name=app_name, path=path), app_name,
                            'app', 'tns_modules')

    @staticmethod
    def get_apk_path(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_platforms_android_folder(app_name=app_name, path=path), 'app', 'build',
                            'outputs', 'apk')

    @staticmethod
    def get_ipa_path(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsPaths.get_platforms_ios_folder(app_name=app_name, path=path), 'build',
                            'Debug-iphonesimulator')

    @staticmethod
    def get_app_ios_path(app_name, path=Settings.TEST_RUN_HOME):
        return ''

    @staticmethod
    def get_bundle_id(app_name):
        return app_name.replace('-', '')
