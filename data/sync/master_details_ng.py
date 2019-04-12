# pylint: disable=too-many-statements

"""
Sync changes on Master-Detail project helper.
"""

import os

from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.tns import Tns


def sync_master_detail_ng(app_name, platform, device, bundle=True, hmr=True, uglify=False, aot=False):
    Tns.run(app_name=app_name, platform=platform, emulator=True, wait=False, bundle=bundle, hmr=hmr, aot=aot,
            uglify=uglify)

    # Verify it looks properly
    device.wait_for_text(text=Changes.MasterDetailNG.TS.old_text, timeout=300, retry_delay=5)
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
