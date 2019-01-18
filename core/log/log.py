import logging
import os

import datetime

from core.settings import Settings


class Log(object):

    @staticmethod
    def log(level, msg):
        if level != logging.DEBUG:
            date = datetime.datetime.now().strftime('%H:%M:%S')
            print('{0} {1}'.format(date, msg))

    @staticmethod
    def debug(message):
        Log.log(logging.DEBUG, message)

    @staticmethod
    def info(message):
        Log.log(logging.INFO, message)

    @staticmethod
    def warning(message):
        Log.log(logging.WARNING, message)

    @staticmethod
    def error(message):
        Log.log(logging.ERROR, message)

    @staticmethod
    def fatal(message):
        Log.log(logging.FATAL, message)

    @staticmethod
    def test_class_start(class_name):
        Log.info('=============================================================')
        Log.info('TEST CLASS:  {0}'.format(class_name))
        Log.info('')

    @staticmethod
    def test_start(test_name):
        Log.info('=============================================================')
        Log.info('START TEST:  {0}'.format(test_name))
        Log.info('')

    @staticmethod
    def test_end(test_name, outcome):
        Log.info('')
        Log.info('TEST COMPLETE:  {0}'.format(test_name))
        Log.info('OUTCOME:  {0}'.format(outcome))
        Log.info('=============================================================')
        Log.info('')

    @staticmethod
    def test_class_end(class_name):
        Log.info('')
        Log.info('END CLASS:  {0}'.format(class_name))
        Log.info('=============================================================')
        Log.info('')

    @staticmethod
    def test_step(message):
        Log.info(message)

    @staticmethod
    def host_screen(image_name):
        path = os.path.join(Settings.TEST_OUT_IMAGES, image_name + '.png')
        Log.debug('Save current host OS image at: ' + path)

    @staticmethod
    def device_screen(image_name, device_id):
        path = os.path.join(Settings.TEST_OUT_IMAGES, image_name + '.png')
        Log.debug('Save screen of {0} at {1}: '.format(device_id, path))

    @staticmethod
    def settings():
        Log.info('==================== General Info ====================')
        Log.info('Host OS: ' + str(Settings.HOST_OS))
        Log.info('Python Version: ' + str(Settings.PYTHON_VERSION))
        Log.info('====================== Packages ======================')
        Log.info('NS CLI: ' + str(Settings.Packages.NS_CLI))
        Log.info('NG CLI: ' + str(Settings.Packages.NG_CLI))
        Log.info('SCHEMATICS: ' + str(Settings.Packages.NS_SCHEMATICS))
        Log.info('Android: ' + str(Settings.Packages.ANDROID))
        Log.info('iOS: ' + str(Settings.Packages.IOS))
        Log.info('Modules: ' + str(Settings.Packages.MODULES))
        Log.info('Angular: ' + str(Settings.Packages.ANGULAR))
        Log.info('Typescript: ' + str(Settings.Packages.TYPESCRIPT))
        Log.info('Webpack: ' + str(Settings.Packages.WEBPACK))
        Log.info('Sass: ' + str(Settings.Packages.SASS))
        Log.info('==================== Executables =====================')
        Log.info('Tns: ' + str(Settings.Executables.TNS))
        Log.info('Ng: ' + str(Settings.Executables.NG))
        Log.info('================== Android Options ===================')
        Log.info('FRAMEWORK_PATH: ' + str(Settings.Android.FRAMEWORK_PATH))
        Log.info('ANDROID_KEYSTORE_ALIAS_PASS: ' + str(Settings.Android.ANDROID_KEYSTORE_ALIAS_PASS))
        Log.info('ANDROID_KEYSTORE_ALIAS: ' + str(Settings.Android.ANDROID_KEYSTORE_ALIAS))
        Log.info('ANDROID_KEYSTORE_PASS: ' + str(Settings.Android.ANDROID_KEYSTORE_PASS))
        Log.info('ANDROID_KEYSTORE_PATH: ' + str(Settings.Android.ANDROID_KEYSTORE_PATH))
        Log.info('==================== iOS Options =====================')
        Log.info('FRAMEWORK_PATH: ' + str(Settings.IOS.FRAMEWORK_PATH))
        Log.info('DEVELOPMENT_TEAM: ' + str(Settings.IOS.DEVELOPMENT_TEAM))
        Log.info('DEV_PROVISION: ' + str(Settings.IOS.DEV_PROVISION))
        Log.info('DISTRIBUTION_PROVISION: ' + str(Settings.IOS.DISTRIBUTION_PROVISION))
        Log.info('======================================================')
