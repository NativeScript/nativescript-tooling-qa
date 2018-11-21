import logging
import os

from core.settings import Settings
from core.utils.json_utils import JsonUtils
from core.utils.npm import Npm
from core.utils.process import Run


class App(object):

    @staticmethod
    def get_package_json(app_name):
        return JsonUtils.read(os.path.join(Settings.TEST_RUN_HOME, app_name, 'package.json'))

    @staticmethod
    def is_dev_dependency(app_name, dependency):
        json = App.get_package_json(app_name=app_name)
        dev_deps = json.get('devDependencies')
        if dev_deps is not None:
            if dev_deps.get(dependency) is not None:
                return True
        return False

    @staticmethod
    def is_dependency(app_name, dependency):
        json = App.get_package_json(app_name=app_name)
        dev_deps = json.get('dependencies')
        if dev_deps is not None:
            if dev_deps.get(dependency) is not None:
                return True
        return False

    @staticmethod
    def install_dependency(app_name, dependency, version='latest'):
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        Npm.uninstall(package=dependency, option='--save', folder=app_path)
        Npm.install(package='{0}@{1}'.format(dependency, version), option='--save', folder=app_path)

    @staticmethod
    def install_dev_dependency(app_name, dependency, version='latest'):
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        Npm.uninstall(package=dependency, option='--save-dev', folder=app_path)
        Npm.install(package='{0}@{1}'.format(dependency, version), option='--save-dev', folder=app_path)

    @staticmethod
    def update(app_name, modules=True, angular=True, typescript=True, web_pack=True, ns_plugins=False):
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        if modules and App.is_dependency(app_name=app_name, dependency='tns-core-modules'):
            Npm.uninstall(package='tns-core-modules', option='--save', folder=app_path)
            Npm.install(package=Settings.Packages.MODULES, option='--save', folder=app_path)
        if angular and App.is_dependency(app_name=app_name, dependency='nativescript-angular'):
            Npm.uninstall(package='nativescript-angular', option='--save', folder=app_path)
            Npm.install(package=Settings.Packages.ANGULAR, option='--save', folder=app_path)
            update_script = os.path.join(app_path, 'node_modules', '.bin', 'update-app-ng-deps')
            result = Run.command(cmd=update_script, log_level=logging.INFO)
            assert 'Angular dependencies updated' in result.output, 'Angular dependencies not updated.'
            Npm.install(folder=app_path)
        if typescript and App.is_dev_dependency(app_name=app_name, dependency='nativescript-dev-typescript'):
            Npm.uninstall(package='nativescript-dev-typescript', option='--save-dev', folder=app_path)
            Npm.install(package=Settings.Packages.TYPESCRIPT, option='--save-dev', folder=app_path)
        if web_pack and App.is_dev_dependency(app_name=app_name, dependency='nativescript-dev-webpack'):
            Npm.uninstall(package='nativescript-dev-webpack', option='--save-dev', folder=app_path)
            Npm.install(package=Settings.Packages.WEBPACK, option='--save-dev', folder=app_path)
            update_script = os.path.join(app_path, 'node_modules', '.bin', 'update-ns-webpack') + ' --deps --configs'
            result = Run.command(cmd=update_script, log_level=logging.INFO)
            assert 'Updating dev dependencies...' in result.output, 'Webpack dependencies not updated.'
            assert 'Updating configuration files...' in result.output, 'Webpack configs not updated.'
            Npm.install(folder=app_path)
        if ns_plugins:
            pass

    @staticmethod
    def ensure_webpack_installed(app_name):
        if not App.is_dev_dependency(app_name=app_name, dependency='nativescript-dev-webpack'):
            Npm.install(package=Settings.Packages.WEBPACK, folder=os.path.join(Settings.TEST_RUN_HOME, app_name))
