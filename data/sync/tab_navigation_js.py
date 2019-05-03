import os

from core.enums.app_type import AppType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


def sync_tab_navigation_js(app_name, platform, device, bundle=True, hmr=True, uglify=False, aot=False,
                        snapshot=False, instrumented=True):
    __sync_tab_navigation_js_ts(app_type=AppType.JS, app_name=app_name, platform=platform,
                             device=device,
                             bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot,
                             instrumented=instrumented)


def sync_tab_navigation_ts(app_name, platform, device, bundle=True, hmr=True, uglify=False, aot=False,
                        snapshot=False, instrumented=True):
    __sync_tab_navigation_js_ts(app_type=AppType.TS, app_name=app_name, platform=platform,
                             device=device,
                             bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot,
                             instrumented=instrumented)


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


def __sync_tab_navigation_js_ts(app_type, app_name, platform, device,
                             bundle=True, hmr=True, uglify=False, aot=False, snapshot=False, instrumented=False):
    # Set changes
    js_file = os.path.basename(Changes.JSTabNavigation.JS.file_path)
    if app_type == AppType.JS:
        js_change = Changes.JSTabNavigation.JS
        xml_change = Changes.JSTabNavigation.XML
        scss_change = Changes.JSTabNavigation.SCSS_VARIABLES
    elif app_type == AppType.TS:
        js_file = os.path.basename(Changes.TSTabNavigation.TS.file_path)
        js_change = Changes.TSTabNavigation.TS
        xml_change = Changes.TSTabNavigation.XML
        scss_change = Changes.TSTabNavigation.SCSS_VARIABLES
    else:
        raise ValueError('Invalid app_type value.')

    # Execute `tns run` and wait until logs are OK
    result = Tns.run(app_name=app_name, platform=platform, emulator=True, wait=False,
                     bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot)
    __verify_snapshot_skipped(snapshot, result)

    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.UNKNOWN, bundle=bundle,
                                   hmr=hmr, instrumented=instrumented, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=240)

    # Verify it looks properly
    device.wait_for_text(text=js_change.old_text)
    device.wait_for_text(text=xml_change.old_text)
    blue_count = device.get_pixels_by_color(color=Colors.LIGHT_BLUE)
    assert blue_count > 100, 'Failed to find blue color on {0}'.format(device.name)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)

    # Edit JS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=js_change)
    device.wait_for_text(text=js_change.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name=js_file, instrumented=instrumented, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Edit XML file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=xml_change)
    device.wait_for_text(text=xml_change.new_text)
    device.wait_for_text(text=js_change.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name='home-items-page.xml', instrumented=instrumented, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Edit SCSS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=scss_change)
    device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count * 2, delta=25)
    device.wait_for_text(text=xml_change.new_text)
    device.wait_for_text(text=js_change.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name='_app-variables.scss', instrumented=instrumented, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Revert all the changes
    Sync.revert(app_name=app_name, change_set=js_change)
    device.wait_for_text(text=js_change.old_text)
    device.wait_for_text(text=xml_change.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name=js_file, instrumented=instrumented, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    Sync.revert(app_name=app_name, change_set=xml_change)
    device.wait_for_text(text=xml_change.old_text)
    device.wait_for_text(text=js_change.old_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name='home-items-page.xml', instrumented=instrumented, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    Sync.revert(app_name=app_name, change_set=scss_change)
    device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count)
    device.wait_for_text(text=xml_change.old_text)
    device.wait_for_text(text=js_change.old_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name='_app-variables.scss', instrumented=instrumented, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Assert final and initial states are same
    device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)
