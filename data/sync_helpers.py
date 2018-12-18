import os

from core.settings import Settings
from core.utils.file_utils import File
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.tns import Tns


class SyncHelpers(object):

    @staticmethod
    def sync_hello_world_js(app_name, platform, device, bundle=False, hmr=False, uglify=False, aot=False,
                            snapshot=False):
        result = Tns.run(app_name=app_name, platform=platform, device=device.id, wait=False,
                         bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot)

        # Verify if snapshot flag is passed it it skipped
        if snapshot:
            msg = 'Bear in mind that snapshot is only available in release builds and is NOT available on Windows'
            skip_snapshot = Wait.until(lambda: 'Stripping the snapshot flag' in File.read(result.log_file), timeout=180)
            assert skip_snapshot, 'Not message that snapshot is skipped.'
            assert msg in File.read(result.log_file), 'No message that snapshot is NOT available on Windows.'

        # Verify it looks properly
        device.wait_for_text(text=Changes.JSHelloWord.JS.old_value, timeout=180, retry_delay=5)
        device.wait_for_text(text=Changes.JSHelloWord.XML.old_value)
        blue_count = device.get_pixels_by_color(color=Colors.LIGHT_BLUE)
        assert blue_count > 100, 'Failed to find blue color on {0}'.format(device.name)
        initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
        device.get_screen(path=initial_state)

        # Edit JS file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.JSHelloWord.JS)
        device.wait_for_text(text=Changes.JSHelloWord.JS.new_value)

        # Edit XML file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.JSHelloWord.XML)
        device.wait_for_text(text=Changes.JSHelloWord.XML.new_value)
        device.wait_for_text(text=Changes.JSHelloWord.JS.new_value)

        # Edit CSS file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.JSHelloWord.CSS)
        device.wait_for_text(text=Changes.JSHelloWord.XML.new_value)
        device.wait_for_text(text=Changes.JSHelloWord.JS.new_value)
        device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count * 2, delta=25)

        # Revert all the changes
        Sync.revert(app_name=app_name, change_set=Changes.JSHelloWord.JS)
        device.wait_for_text(text=Changes.JSHelloWord.JS.old_value)
        device.wait_for_text(text=Changes.JSHelloWord.XML.new_value)

        Sync.revert(app_name=app_name, change_set=Changes.JSHelloWord.XML)
        device.wait_for_text(text=Changes.JSHelloWord.XML.old_value)
        device.wait_for_text(text=Changes.JSHelloWord.JS.old_value)

        Sync.revert(app_name=app_name, change_set=Changes.JSHelloWord.CSS)
        device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count)
        device.wait_for_text(text=Changes.JSHelloWord.XML.old_value)
        device.wait_for_text(text=Changes.JSHelloWord.JS.old_value)

        # Assert final and initial states are same
        device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)

    @staticmethod
    def sync_hello_world_ts(app_name, platform, device, bundle=False, hmr=False, uglify=False, aot=False,
                            snapshot=False):
        result = Tns.run(app_name=app_name, platform=platform, device=device.id, wait=False,
                         bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot)

        # Verify if snapshot flag is passed it it skipped
        if snapshot:
            msg = 'Bear in mind that snapshot is only available in release builds and is NOT available on Windows'
            skip_snapshot = Wait.until(lambda: 'Stripping the snapshot flag' in File.read(result.log_file), timeout=180)
            assert skip_snapshot, 'Not message that snapshot is skipped.'
            assert msg in File.read(result.log_file), 'No message that snapshot is NOT available on Windows.'

        # Verify it looks properly
        device.wait_for_text(text=Changes.TSHelloWord.TS.old_value, timeout=180, retry_delay=5)
        device.wait_for_text(text=Changes.TSHelloWord.XML.old_value)
        blue_count = device.get_pixels_by_color(color=Colors.LIGHT_BLUE)
        assert blue_count > 100, 'Failed to find blue color on {0}'.format(device.name)
        initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
        device.get_screen(path=initial_state)

        # Edit JS file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.TSHelloWord.TS)
        device.wait_for_text(text=Changes.TSHelloWord.TS.new_value)

        # Edit XML file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.TSHelloWord.XML)
        device.wait_for_text(text=Changes.TSHelloWord.XML.new_value)
        device.wait_for_text(text=Changes.TSHelloWord.TS.new_value)

        # Edit CSS file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.TSHelloWord.CSS)
        device.wait_for_text(text=Changes.TSHelloWord.XML.new_value)
        device.wait_for_text(text=Changes.TSHelloWord.TS.new_value)
        device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count * 2, delta=25)

        # Revert all the changes
        Sync.revert(app_name=app_name, change_set=Changes.TSHelloWord.TS)
        device.wait_for_text(text=Changes.TSHelloWord.TS.old_value)
        device.wait_for_text(text=Changes.TSHelloWord.XML.new_value)

        Sync.revert(app_name=app_name, change_set=Changes.TSHelloWord.XML)
        device.wait_for_text(text=Changes.TSHelloWord.XML.old_value)
        device.wait_for_text(text=Changes.TSHelloWord.TS.old_value)

        Sync.revert(app_name=app_name, change_set=Changes.TSHelloWord.CSS)
        device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count)
        device.wait_for_text(text=Changes.TSHelloWord.XML.old_value)
        device.wait_for_text(text=Changes.TSHelloWord.TS.old_value)

        # Assert final and initial states are same
        device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)

    @staticmethod
    def sync_hello_world_ng(app_name, platform, device, bundle=False, uglify=False, aot=False):
        Tns.run(app_name=app_name, platform=platform, device=device.id, wait=False, bundle=bundle, aot=aot,
                uglify=uglify)

        # Verify it looks properly
        device.wait_for_text(text=Changes.NGHelloWorld.TS.old_value, timeout=60, retry_delay=5)
        device.wait_for_main_color(color=Colors.WHITE)
        initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
        device.get_screen(path=initial_state)

        # Apply changes
        Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
        device.wait_for_text(text=Changes.NGHelloWorld.TS.new_value)

        Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
        assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_value)

        Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
        device.wait_for_main_color(color=Colors.DARK)
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
        assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_value)

        # Revert changes
        Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
        device.wait_for_text(text=Changes.NGHelloWorld.TS.new_value)

        Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
        device.wait_for_text(text=Changes.NGHelloWorld.TS.old_value)
        device.wait_for_main_color(color=Colors.DARK)

        Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
        device.wait_for_main_color(color=Colors.WHITE)
        device.wait_for_text(text=Changes.NGHelloWorld.TS.old_value)

        # Assert final and initial states are same
        device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)

    @staticmethod
    def sync_master_detail_ng(app_name, platform, device, bundle=False, uglify=False, aot=False):
        Tns.run(app_name=app_name, platform=platform, device=device.id, wait=False, bundle=bundle, aot=aot,
                uglify=uglify)

        # Verify it looks properly
        device.wait_for_text(text=Changes.MasterDetailNG.TS.old_value, timeout=60, retry_delay=5)
        device.wait_for_main_color(color=Colors.WHITE)

        initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
        device.get_screen(path=initial_state)

        # Edit TS file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.MasterDetailNG.TS)
        device.wait_for_text(text=Changes.MasterDetailNG.TS.new_value)

        # Edit HTML file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.MasterDetailNG.HTML)
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
        assert not device.is_text_visible(text=Changes.MasterDetailNG.TS.new_value)

        # Edit CSS file and verify changes are applied
        Sync.replace(app_name=app_name, change_set=Changes.MasterDetailNG.CSS)
        device.wait_for_main_color(color=Colors.DARK)
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
        assert not device.is_text_visible(text=Changes.MasterDetailNG.TS.new_value)

        # Revert HTML
        Sync.revert(app_name=app_name, change_set=Changes.MasterDetailNG.HTML)
        device.wait_for_text(text=Changes.MasterDetailNG.TS.new_value)

        # Revert TS
        Sync.revert(app_name=app_name, change_set=Changes.MasterDetailNG.TS)
        device.wait_for_text(text=Changes.MasterDetailNG.TS.old_value)
        device.wait_for_main_color(color=Colors.DARK)

        # Revert CSS
        Sync.revert(app_name=app_name, change_set=Changes.MasterDetailNG.CSS)
        device.wait_for_main_color(color=Colors.WHITE)
        device.wait_for_text(text=Changes.MasterDetailNG.TS.old_value)

        # Assert final and initial states are same
        device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)
