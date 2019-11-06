"""
Tests for 'resources generate' icons and splashes
"""

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_assert import TnsAssert

APP_NAME = Settings.AppName.DEFAULT


# noinspection PyMethodMayBeStatic
class ResourcesUpdateTests(TnsTest):

    def test_300_tns_resources_update(self):
        # Create nativescript@3 app
        result = Tns.create(app_name=APP_NAME, template='tns-template-hello-world@3.0', verify=False, update=False)
        TnsAssert.created(app_name=APP_NAME, output=result.output, webpack=False, theme=False)

        # Update resources
        out = Tns.exec_command(command='resources update', path=APP_NAME).output
        assert "Successfully updated your project's application resources '/Android' directory structure." in out
        assert "The previous version of your Android application resources has been renamed to '/Android-Pre-v4'" in out

    def test_301_tns_resources_update_on_updated_project(self):
        result = Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package,
                            verify=False, update=False)
        TnsAssert.created(app_name=APP_NAME, output=result.output, webpack=False, theme=False)
        result = Tns.exec_command(command='resources update', path=APP_NAME)
        assert 'The App_Resources have already been updated for the Android platform.' in result.output
