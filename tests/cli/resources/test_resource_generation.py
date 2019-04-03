"""
Tests for 'resources generate' icons and splashes
"""
import os

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_assert import TnsAssert

APP_NAME = Settings.AppName.DEFAULT


# noinspection PyMethodMayBeStatic
class ResourcesGenerateTests(TnsTest):
    resources = os.path.join(Settings.ASSETS_HOME, 'resources')
    expected_images_android = os.path.join(resources, 'android')
    expected_images_ios = os.path.join(resources, 'ios')
    star_image = os.path.join(resources, 'star.png')

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_001_tns_resources_generate_icons(self):
        command = 'resources generate icons {0}'.format(self.star_image)
        result = Tns.exec_command(command=command, path=APP_NAME)
        assert 'Generating icons' in result.output
        assert 'Icons generation completed' in result.output
        assert 'Invalid settings specified for the resizer' not in result.output

    def test_200_tns_resources_generate_splashes(self):
        command = 'resources generate splashes {0} --background green'.format(self.star_image)
        result = Tns.exec_command(command=command, path=APP_NAME)
        assert 'Generating splash screens' in result.output
        assert 'Splash screens generation completed' in result.output

    def test_300_tns_resources_generate_icons_apetools(self):
        # Test for https://github.com/NativeScript/nativescript-cli/issues/3666

        # Simulate resources generated with apetools
        # TODO: Implement it!

        # Generate icons with nativescript
        self.test_001_tns_resources_generate_icons()

    def test_301_tns_resources_generate_icons_old_template_structure(self):
        # Create nativescript@4 app
        result = Tns.create(app_name=APP_NAME, template='tns-template-hello-world@4.0', verify=False)
        TnsAssert.created(app_name=APP_NAME, output=result.output, webpack=False)

        # Generate icons with nativescript
        self.test_001_tns_resources_generate_icons()
