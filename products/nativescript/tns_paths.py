# pylint: disable=unused-argument
# TODO: Implement it!
import os

from core.settings import Settings


# noinspection PyUnusedLocal
from core.settings.Settings import AppName


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


# class Paths(object):
#
#     @staticmethod
#     def platforms(app_name):
#         NODE_MODULES = 'node_modules'
#         TNS_MODULES = os.path.join(NODE_MODULES, 'tns-core-modules')
#         HOOKS = 'hooks'
#         PLATFORM_IOS = os.path.join('platforms', 'ios/')
#         PLATFORM_IOS_APP_PATH = os.path.join(PLATFORM_IOS, 'build', 'Debug-iphonesimulator')
#         PLATFORM_ANDROID = os.path.join('platforms', 'android/')
#         PLATFORM_ANDROID_BUILD = os.path.join(PLATFORM_ANDROID, 'app', 'build')
#         PLATFORM_ANDROID_APK_PATH = os.path.join(PLATFORM_ANDROID_BUILD, 'outputs', 'apk')
#         PLATFORM_ANDROID_APK_RELEASE_PATH = os.path.join(PLATFORM_ANDROID_BUILD, 'outputs', 'apk', 'release')
#         PLATFORM_ANDROID_APK_DEBUG_PATH = os.path.join(PLATFORM_ANDROID_BUILD, 'outputs', 'apk', 'debug')
#         PLATFORM_ANDROID_SRC_MAIN_PATH = os.path.join(PLATFORM_ANDROID, 'app', 'src', 'main/')
#         PLATFORM_ANDROID_APP_PATH = os.path.join(PLATFORM_ANDROID_SRC_MAIN_PATH, 'assets', 'app/')
#         PLATFORM_ANDROID_NPM_MODULES_PATH = os.path.join(PLATFORM_ANDROID_APP_PATH, 'tns_modules/')
#         PLATFORM_ANDROID_TNS_MODULES_PATH = os.path.join(PLATFORM_ANDROID_NPM_MODULES_PATH, 'tns-core-modules/')
#         PLATFORM_IOS_NPM_MODULES_PATH = os.path.join(PLATFORM_IOS, app_name, 'app', 'tns_modules')
#
#     @staticmethod
#     def plugin_name(app_name, plugin_name):
#         tns_plugin = os.path.join(app_name, 'node_modules', 'tns-plugin')
#         tns_plugin_platform_ios = os.path.join(app_name, 'platforms', 'ios', app_name, 'app', 'tns_modules',
#                                                'tns-plugin')
#         # PLATFORM_IOS_NPM_MODULES_PATH = os.path.join(PLATFORM_IOS, AppName.DEFAULT, 'app', 'tns_modules')
#         # tns_plugin = os.path.join(AppName.DEFAULT, 'node_modules', 'tns-plugin')
#         # tns_plugin_platform_ios = os.path.join(AppName.DEFAULT, 'platforms', 'ios', 'TestApp', 'app', 'tns_modules',
#         #                                        'tns-plugin')
