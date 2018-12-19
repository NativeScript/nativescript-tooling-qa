import os

from core.settings import Settings
from core.utils.file_utils import File
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from enums.app_type import AppType
from enums.platform_type import Platform
from log.log import Log
from products.nativescript.tns import Tns


class SyncHelpers(object):

    @staticmethod
    def sync_hello_world_js(app_name, platform, device, bundle=False, hmr=False, uglify=False, aot=False,
                            snapshot=False):
        SyncHelpers.__sync_hello_world_js_ts(app_type=AppType.JS, app_name=app_name, platform=platform, device=device,
                                             bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot)

    @staticmethod
    def sync_hello_world_ts(app_name, platform, device, bundle=False, hmr=False, uglify=False, aot=False,
                            snapshot=False):
        SyncHelpers.__sync_hello_world_js_ts(app_type=AppType.TS, app_name=app_name, platform=platform, device=device,
                                             bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot)

    @staticmethod
    def sync_hello_world_ng(app_name, platform, device, bundle=False, uglify=False, aot=False):
        Tns.run(app_name=app_name, platform=platform, device=device.id, wait=False,
                bundle=bundle, aot=aot, uglify=uglify)

        # Verify it looks properly
        device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text, timeout=60, retry_delay=5)
        device.wait_for_main_color(color=Colors.WHITE)
        initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
        device.get_screen(path=initial_state)

        # Apply changes
        Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
        device.wait_for_text(text=Changes.NGHelloWorld.TS.new_text)

        Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
        assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)

        Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
        device.wait_for_main_color(color=Colors.DARK)
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
        assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)

        # Revert changes
        Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
        device.wait_for_text(text=Changes.NGHelloWorld.TS.new_text)

        Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
        device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)
        device.wait_for_main_color(color=Colors.DARK)

        Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
        device.wait_for_main_color(color=Colors.WHITE)
        device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)

        # Assert final and initial states are same
        device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)

    @staticmethod
    def sync_master_detail_ng(app_name, platform, device, bundle=False, uglify=False, aot=False):
        Tns.run(app_name=app_name, platform=platform, device=device.id, wait=False, bundle=bundle, aot=aot,
                uglify=uglify)

        # Verify it looks properly
        device.wait_for_text(text=Changes.MasterDetailNG.TS.old_text, timeout=60, retry_delay=5)
        device.wait_for_text(text=Changes.MasterDetailNG.HTML.old_text, timeout=30)
        device.wait_for_main_color(color=Colors.WHITE)

        initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
        device.get_screen(path=initial_state)

        # Edit TS file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.MasterDetailNG.TS)
        device.wait_for_text(text=Changes.MasterDetailNG.TS.new_text)

        # Edit HTML file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.MasterDetailNG.HTML)
        device.wait_for_text(text=Changes.MasterDetailNG.HTML.new_text)
        device.wait_for_text(text=Changes.MasterDetailNG.TS.new_text)

        # Edit common SCSS on root level
        change = Changes.MasterDetailNG.SCSS_ROOT_COMMON
        Sync.replace(app_name=app_name, change_set=change)
        assert Wait.until(lambda: device.get_pixels_by_color(color=change.new_color) > 100), \
            'Common SCSS on root level not applied!'
        Log.info('Common SCSS on root level applied successfully!')

        # Edit platform specific SCSS on root level
        if platform == Platform.ANDROID:
            change = Changes.MasterDetailNG.SCSS_ROOT_ANDROID
        elif platform == Platform.IOS:
            change = Changes.MasterDetailNG.SCSS_ROOT_IOS
        else:
            raise ValueError('Invalid platform value!')
        Sync.replace(app_name=app_name, change_set=change)
        assert Wait.until(lambda: device.get_pixels_by_color(color=change.new_color) > 100), \
            'Platform specific SCSS on root level not applied!'
        Log.info('Platform specific SCSS on root level applied successfully!')

        # Edit nested common SCSS
        change = Changes.MasterDetailNG.SCSS_NESTED_COMMON
        Sync.replace(app_name=app_name, change_set=change)
        assert Wait.until(lambda: device.get_pixels_by_color(color=change.new_color) > 100), \
            'Common nested SCSS not applied!'
        Log.info('Common nested SCSS applied successfully!')

        # Edit nested platform specific SCSS
        if platform == Platform.ANDROID:
            change = Changes.MasterDetailNG.SCSS_NESTED_ANDROID
        elif platform == Platform.IOS:
            change = Changes.MasterDetailNG.SCSS_NESTED_IOS
        else:
            raise ValueError('Invalid platform value!')
        Sync.replace(app_name=app_name, change_set=change)
        assert Wait.until(lambda: device.get_pixels_by_color(color=change.new_color) > 100), \
            'Platform specific nested SCSS not applied!'
        Log.info('Platform specific nested SCSS applied successfully!')

        # Revert TS file and verify changes are applied
        Sync.revert(app_name=app_name, change_set=Changes.MasterDetailNG.TS)
        device.wait_for_text(text=Changes.MasterDetailNG.TS.old_text)
        device.wait_for_text(text=Changes.MasterDetailNG.HTML.new_text)

        # Revert HTML file and verify changes are applied
        Sync.revert(app_name=app_name, change_set=Changes.MasterDetailNG.HTML)
        device.wait_for_text(text=Changes.MasterDetailNG.HTML.old_text)
        device.wait_for_text(text=Changes.MasterDetailNG.TS.old_text)

        # Revert common SCSS on root level
        change = Changes.MasterDetailNG.SCSS_ROOT_COMMON
        Sync.revert(app_name=app_name, change_set=change)
        assert Wait.until(lambda: device.get_pixels_by_color(color=change.new_color) < 100), \
            'Common SCSS on root level not reverted!'
        Log.info('Common SCSS on root level reverted successfully!')

        # Revert platform specific SCSS on root level
        if platform == Platform.ANDROID:
            change = Changes.MasterDetailNG.SCSS_ROOT_ANDROID
        elif platform == Platform.IOS:
            change = Changes.MasterDetailNG.SCSS_ROOT_IOS
        else:
            raise ValueError('Invalid platform value!')
        Sync.revert(app_name=app_name, change_set=change)
        assert Wait.until(lambda: device.get_pixels_by_color(color=change.new_color) < 100), \
            'Platform specific SCSS on root level not reverted!'
        Log.info('Platform specific SCSS on root level reverted successfully!')

        # Revert nested common SCSS
        change = Changes.MasterDetailNG.SCSS_NESTED_COMMON
        Sync.revert(app_name=app_name, change_set=change)
        assert Wait.until(lambda: device.get_pixels_by_color(color=change.new_color) < 100), \
            'Common SCSS on root level not applied!'
        Log.info('Platform specific SCSS on root level reverted successfully!')

        # Revert nested platform specific SCSS
        if platform == Platform.ANDROID:
            change = Changes.MasterDetailNG.SCSS_NESTED_ANDROID
        elif platform == Platform.IOS:
            change = Changes.MasterDetailNG.SCSS_NESTED_IOS
        else:
            raise ValueError('Invalid platform value!')
        Sync.revert(app_name=app_name, change_set=change)
        assert Wait.until(lambda: device.get_pixels_by_color(color=change.new_color) < 100), \
            'Platform specific SCSS on root level not applied!'

        # Assert final and initial states are same
        device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)

    @staticmethod
    def __verify_snapshot_skipped(snapshot, result):
        """
        Verify if snapshot flag is passed it it skipped.
        :param snapshot: True if snapshot flag is present.
        :param result: Result of `tns run` command.
        """
        if snapshot:
            msg = 'Bear in mind that snapshot is only available in release builds and is NOT available on Windows'
            skip_snapshot = Wait.until(lambda: 'Stripping the snapshot flag' in File.read(result.log_file), timeout=180)
            assert skip_snapshot, 'Not message that snapshot is skipped.'
            assert msg in File.read(result.log_file), 'No message that snapshot is NOT available on Windows.'

    @staticmethod
    def __sync_hello_world_js_ts(app_type, app_name, platform, device,
                                 bundle=False, hmr=False, uglify=False, aot=False, snapshot=False):

        if app_type == AppType.JS:
            js_change = Changes.JSHelloWord.JS
            xml_change = Changes.JSHelloWord.XML
            css_change = Changes.JSHelloWord.CSS
        elif app_type == AppType.TS:
            js_change = Changes.TSHelloWord.TS
            xml_change = Changes.TSHelloWord.XML
            css_change = Changes.TSHelloWord.CSS
        else:
            raise ValueError('Invalid app_type value.')

        result = Tns.run(app_name=app_name, platform=platform, device=device.id, wait=False,
                         bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot)

        SyncHelpers.__verify_snapshot_skipped(snapshot, result)

        # Verify it looks properly
        device.wait_for_text(text=js_change.old_text, timeout=120, retry_delay=5)
        device.wait_for_text(text=xml_change.old_text)
        blue_count = device.get_pixels_by_color(color=Colors.LIGHT_BLUE)
        assert blue_count > 100, 'Failed to find blue color on {0}'.format(device.name)
        initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
        device.get_screen(path=initial_state)

        # Edit JS file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=js_change)
        device.wait_for_text(text=js_change.new_text)

        # Edit XML file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=xml_change)
        device.wait_for_text(text=xml_change.new_text)
        device.wait_for_text(text=js_change.new_text)

        # Edit CSS file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=css_change)
        device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count * 2, delta=25)
        device.wait_for_text(text=xml_change.new_text)
        device.wait_for_text(text=js_change.new_text)

        # Revert all the changes
        Sync.revert(app_name=app_name, change_set=js_change)
        device.wait_for_text(text=js_change.old_text)
        device.wait_for_text(text=xml_change.new_text)

        Sync.revert(app_name=app_name, change_set=xml_change)
        device.wait_for_text(text=xml_change.old_text)
        device.wait_for_text(text=js_change.old_text)

        Sync.revert(app_name=app_name, change_set=css_change)
        device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count)
        device.wait_for_text(text=xml_change.old_text)
        device.wait_for_text(text=js_change.old_text)

        # Assert final and initial states are same
        device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)
