import os

from core.enums.app_type import AppType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.wait import Wait
from core.log.log import Log
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


def sync_tab_navigation_js(app_name,
                           platform,
                           device,
                           bundle=True,
                           hmr=True,
                           uglify=False,
                           aot=False,
                           snapshot=False,
                           instrumented=False,
                           release=False):
    __sync_tab_navigation_js_ts(
        app_type=AppType.JS,
        app_name=app_name,
        platform=platform,
        device=device,
        release=release,
        bundle=bundle,
        hmr=hmr,
        uglify=uglify,
        aot=aot,
        snapshot=snapshot,
        instrumented=instrumented)


def sync_tab_navigation_ts(app_name,
                           platform,
                           device,
                           bundle=True,
                           hmr=True,
                           uglify=False,
                           aot=False,
                           snapshot=False,
                           instrumented=True):
    __sync_tab_navigation_js_ts(
        app_type=AppType.TS,
        app_name=app_name,
        platform=platform,
        device=device,
        bundle=bundle,
        hmr=hmr,
        uglify=uglify,
        aot=aot,
        snapshot=snapshot,
        instrumented=instrumented)


def __sync_tab_navigation_js_ts(app_type,
                                app_name,
                                platform,
                                device,
                                release=False,
                                bundle=True,
                                hmr=True,
                                uglify=False,
                                aot=False,
                                snapshot=False,
                                instrumented=False):
    # Set changes
    js_file = os.path.basename(Changes.JSTabNavigation.JS.file_path)
    if app_type == AppType.JS:
        js_change = Changes.JSTabNavigation.JS
        xml_change = Changes.JSTabNavigation.XML
        scss_change = Changes.JSTabNavigation.SCSS_VARIABLES
        scss_android = Changes.JSTabNavigation.SCSS_ROOT_ANDROID
        scss_ios = Changes.JSTabNavigation.SCSS_ROOT_IOS
    elif app_type == AppType.TS:
        js_file = os.path.basename(Changes.TSTabNavigation.TS.file_path)
        js_change = Changes.TSTabNavigation.TS
        xml_change = Changes.TSTabNavigation.XML
        scss_change = Changes.TSTabNavigation.SCSS_VARIABLES
        scss_android = Changes.TSTabNavigation.SCSS_ROOT_ANDROID
        scss_ios = Changes.TSTabNavigation.SCSS_ROOT_IOS
    else:
        raise ValueError('Invalid app_type value.')

    # Execute `tns run` and wait until logs are OK
    result = Tns.run(
        app_name=app_name,
        platform=platform,
        emulator=True,
        wait=False,
        bundle=bundle,
        hmr=hmr,
        uglify=uglify,
        aot=aot,
        snapshot=snapshot,
        release=release)

    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.UNKNOWN,
        bundle=bundle,
        hmr=hmr,
        instrumented=instrumented,
        device=device)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=240)

    # Verify it looks properly
    device.wait_for_text(text=js_change.old_text)
    device.wait_for_text(text=xml_change.old_text)
    color_count = device.get_pixels_by_color(color=Colors.ACCENT_DARK)
    assert color_count > 100, 'Failed to find ACCENT_DARK color on {0}'.format(
        device.name)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name,
                                 'initial_state.png')
    device.get_screen(path=initial_state)

    # Edit JS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=js_change)
    device.wait_for_text(text=js_change.new_text)
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        hmr=hmr,
        file_name=js_file,
        device=device,
        instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Edit XML file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=xml_change)
    device.wait_for_text(text=xml_change.new_text)
    device.wait_for_text(text=js_change.new_text)
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        hmr=hmr,
        file_name='home-items-page.xml',
        device=device,
        instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Edit SCSS file and verify changes are applied
    # https://github.com/NativeScript/NativeScript/issues/6953
    # Navigate to Browse tab and verify when scss is synced navigation is preserved
    device.click(text="Browse")
    assert not device.is_text_visible(text=js_change.new_text)
    Sync.replace(app_name=app_name, change_set=scss_change)
    assert Wait.until(lambda: device.get_pixels_by_color(color=Colors.RED) > 100), \
        'SCSS not applied!'
    # Verify navigation is preserved and you are still on Browse tab
    assert device.is_text_visible(text="Browse page content goes here"), \
        'Navigation is not preserved when syncing scss/css file!'

    # Edit platform specific SCSS on root level
    if platform == Platform.ANDROID:
        change = scss_android
    elif platform == Platform.IOS:
        change = scss_ios
    else:
        raise ValueError('Invalid platform value!')
    Sync.replace(app_name=app_name, change_set=change)
    assert Wait.until(lambda: device.get_pixels_by_color(color=change.new_color) > 100), \
        'Platform specific SCSS on root level not applied!'
    Log.info('Platform specific SCSS on root level applied successfully!')

    # Revert all the changes in app
    # Navigate to Home tab again
    device.click(text="Home")
    Sync.revert(app_name=app_name, change_set=js_change)
    device.wait_for_text(text=js_change.old_text)
    device.wait_for_text(text=xml_change.new_text)
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        hmr=hmr,
        file_name=js_file,
        device=device,
        instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    Sync.revert(app_name=app_name, change_set=xml_change)
    device.wait_for_text(text=xml_change.old_text)
    device.wait_for_text(text=js_change.old_text)
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        hmr=hmr,
        file_name='home-items-page.xml',
        device=device,
        instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    Sync.revert(app_name=app_name, change_set=scss_change)
    assert Wait.until(lambda: device.get_pixels_by_color(color=Colors.RED) < 100), \
        'SCSS not applied!'
    device.wait_for_text(text=xml_change.old_text)
    device.wait_for_text(text=js_change.old_text)

    Sync.revert(app_name=app_name, change_set=change)
    assert Wait.until(lambda: device.get_pixels_by_color(color=change.new_color) < 100), \
        'Platform specific SCSS on root level not reverted!'
    Log.info('Platform specific SCSS on root level reverted successfully!')

    # Assert final and initial states are same
    device.screen_match(
        expected_image=initial_state, tolerance=1.0, timeout=30)
