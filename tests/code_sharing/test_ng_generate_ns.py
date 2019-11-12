"""
Tests for `ng g` in context of NativeScript only application.
"""
import unittest

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.file_utils import Folder
from products.angular.ng import NG, NS_SCHEMATICS
from products.nativescript.tns_assert import TnsAssert
from products.nativescript.tns_paths import TnsPaths


# noinspection PyMethodMayBeStatic
class NGGenerateNGTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_path = TnsPaths.get_app_path(app_name=app_name)

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        NG.kill()
        Folder.clean(cls.app_path)

        # Create app
        NG.new(collection=NS_SCHEMATICS, project=cls.app_name, shared=False)
        # TODO: Rollback theme=False when schematics use @nativescript/theme
        TnsAssert.created(app_name=cls.app_name, app_data=None, theme=False)

    def setUp(self):
        TnsTest.setUpClass()
        NG.kill()

    def tearDown(self):
        NG.kill()
        TnsTest.tearDown(self)

    def test_001_generate_component(self):
        result = NG.exec_command(command='g c component-test', cwd=self.app_path)
        assert 'CREATE app/component-test/component-test.component.html' in result.output
        assert 'CREATE app/component-test/component-test.component.ts' in result.output
        assert 'CREATE app/component-test/component-test.component.css' in result.output
        assert 'UPDATE app/app.module.ts' in result.output

    def test_002_generate_module(self):
        result = NG.exec_command(command='g m module-test', cwd=self.app_path)
        assert 'CREATE app/module-test/module-test.module.ts' in result.output

    def test_003_generate_component_in_existing_modules(self):
        result = NG.exec_command(command='g m module-test2', cwd=self.app_path)
        assert 'CREATE app/module-test2/module-test2.module.ts' in result.output

        result = NG.exec_command(command='g c module-test2/component-name', cwd=self.app_path)
        assert 'CREATE app/module-test2/component-name/component-name.component.html' in result.output
        assert 'CREATE app/module-test2/component-name/component-name.component.ts' in result.output
        assert 'CREATE app/module-test2/component-name/component-name.component.css' in result.output
        assert 'UPDATE app/module-test2/module-test2.module.ts' in result.output

    @unittest.skip('Skip because of https://github.com/NativeScript/nativescript-schematics/issues/194')
    def test_004_generate_master_detail(self):
        result = NG.exec_command(command='g master-detail --master=dogs --detail=dog', cwd=self.app_path)
        assert 'CREATE app/dogs/dog-detail/dog-detail.component.html' in result.output
        assert 'CREATE app/dogs/dogs/dogs.component.html' in result.output
        assert 'data.service.ts' in result.output
        assert 'dogs.module.ts' in result.output
