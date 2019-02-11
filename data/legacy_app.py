import os

from core.enums.app_type import AppType
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.npm import Npm
from products.nativescript.app import App
from products.nativescript.tns import Tns


class LegacyApp(object):
    @staticmethod
    def create(app_name, app_type):
        """
         Create hello-world app based on {N} 4.2
        :param app_name: App name.
        :param app_type: AppType enum value.
        """
        template = 'tns-template-hello-world'
        if app_type == AppType.NG:
            template = template + '-ng'
        if app_type == AppType.TS:
            template = template + '-ts'
        Tns.create(app_name=app_name, template='{0}@4.2'.format(template), update=False, verify=False)
        assert '~4.2.' in App.get_package_json(app_name=app_name).get('dependencies').get('tns-core-modules')
        if app_type == AppType.NG:
            assert '~6.1.' in App.get_package_json(app_name=app_name).get('dependencies').get('nativescript-angular')
            assert '~6.1.' in App.get_package_json(app_name=app_name).get('dependencies').get('@angular/core')
        # Add platforms
        Tns.platform_add_android(app_name=app_name, version='4.2')
        if Settings.HOST_OS == OSType.OSX:
            Tns.platform_add_ios(app_name=app_name, version='4.2')
        # Install webpack (it was not included in {N} 4.2 templates)
        Npm.install(package='nativescript-dev-webpack@0.16', option='--save-dev',
                    folder=os.path.join(Settings.TEST_RUN_HOME, app_name))
        Npm.install(folder=os.path.join(Settings.TEST_RUN_HOME, app_name))
