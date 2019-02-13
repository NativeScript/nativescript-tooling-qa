"""
Sync changes on JS/TS project helper.
"""

import os

from core.enums.app_type import AppType
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs
from products.nativescript.preview_helpers import Preview

def sync_hello_world_js(app_name, platform, device, bundle=False, hmr=False, uglify=False, aot=False,
                        snapshot=False, instrumented=True):
    __sync_hello_world_js_ts(app_type=AppType.JS, app_name=app_name, platform=platform,
                             device=device,
                             bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot,
                             instrumented=instrumented)


def sync_hello_world_ts(app_name, platform, device, bundle=False, hmr=False, uglify=False, aot=False,
                        snapshot=False, instrumented=False):
    __sync_hello_world_js_ts(app_type=AppType.TS, app_name=app_name, platform=platform,
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


def __sync_hello_world_js_ts(app_type, app_name, platform, device,
                             bundle=False, hmr=False, uglify=False, aot=False, snapshot=False, instrumented=False):
    # Set changes
    js_file = os.path.basename(Changes.JSHelloWord.JS.file_path)
    if app_type == AppType.JS:
        js_change = Changes.JSHelloWord.JS
        xml_change = Changes.JSHelloWord.XML
        css_change = Changes.JSHelloWord.CSS
    elif app_type == AppType.TS:
        js_file = os.path.basename(Changes.TSHelloWord.TS.file_path)
        js_change = Changes.TSHelloWord.TS
        xml_change = Changes.TSHelloWord.XML
        css_change = Changes.TSHelloWord.CSS
    else:
        raise ValueError('Invalid app_type value.')

    # Execute `tns run` and wait until logs are OK
    result = Tns.run(app_name=app_name, platform=platform, emulator=True, wait=False,
                     bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot)
    __verify_snapshot_skipped(snapshot, result)

    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.FULL, bundle=bundle,
                                   hmr=hmr, instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180)

    # Verify it looks properly
    device.wait_for_text(text=js_change.old_text, timeout=60, retry_delay=5)
    device.wait_for_text(text=xml_change.old_text)
    blue_count = device.get_pixels_by_color(color=Colors.LIGHT_BLUE)
    assert blue_count > 100, 'Failed to find blue color on {0}'.format(device.name)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)

    # Edit JS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=js_change)
    device.wait_for_text(text=js_change.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name=js_file, instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Edit XML file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=xml_change)
    device.wait_for_text(text=xml_change.new_text)
    device.wait_for_text(text=js_change.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name='main-page.xml', instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Edit CSS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=css_change)
    device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count * 2, delta=25)
    device.wait_for_text(text=xml_change.new_text)
    device.wait_for_text(text=js_change.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name='app.css', instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Revert all the changes
    Sync.revert(app_name=app_name, change_set=js_change)
    device.wait_for_text(text=js_change.old_text)
    device.wait_for_text(text=xml_change.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name=js_file, instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    Sync.revert(app_name=app_name, change_set=xml_change)
    device.wait_for_text(text=xml_change.old_text)
    device.wait_for_text(text=js_change.old_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name='main-page.xml', instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    Sync.revert(app_name=app_name, change_set=css_change)
    device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count)
    device.wait_for_text(text=xml_change.old_text)
    device.wait_for_text(text=js_change.old_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, file_name='app.css', instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Assert final and initial states are same
    device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)

def preview_hello_world_js_ts(app_name, platform, device, bundle=False, hmr=False, uglify=False, aot=False,\
                            instrumented=False):
    result = Tns.preview(app_name)

    # Read the log and extract the url to load the app on emulator
    log = File.read(result.log_file)
    url = Preview.get_url(log)
    Preview.run_app(url, device.id, platform)

    # Verify logs
    strings = TnsLogs.preview_initial_messages(platform=platform, hmr=hmr, bundle=bundle)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Verify app looks properly
    device.wait_for_text(text=Changes.JSHelloWord.JS.old_text, timeout=60, retry_delay=5)
    device.wait_for_text(text=Changes.JSHelloWord.XML.old_text, timeout=30)
    device.wait_for_main_color(color=Colors.WHITE)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)
