# pylint: disable=unused-argument
# TODO: Implement it!
import os

from core.settings import Settings


# noinspection PyUnusedLocal
class TnsHelpers(object):

    @staticmethod
    def get_app_path(app_name):
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        return app_path

    @staticmethod
    def get_apk(app_name):
        return ''

    @staticmethod
    def get_ipa(app_name):
        return ''

    @staticmethod
    def get_app(app_name):
        return ''
