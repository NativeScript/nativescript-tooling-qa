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
    def get_apk(app_name):
        return ''

    @staticmethod
    def get_ipa(app_name):
        return ''

    @staticmethod
    def get_app(app_name):
        return ''

    @staticmethod
    def get_bundle_id(app_name):
        return app_name.replace('-', '')
