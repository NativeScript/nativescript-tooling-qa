"""
Sync changes on NG project helper.
"""

import os
import time

from core.enums.app_type import AppType
from core.enums.device_type import DeviceType
from core.enums.platform_type import Platform
from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.preview_helpers import Preview
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


def run_hello_world_ng(app_name, platform, device, bundle=True, uglify=False, aot=False, hmr=True,
                       instrumented=True, release=False, snapshot=False):
    # Define if it should be executed on device or emulator
    emulator = True
    device_id = None
    if device.type == DeviceType.ANDROID or device.type == DeviceType.IOS:
        emulator = False
        device_id = device.id

    # Execute tns run command
    result = Tns.run(app_name=app_name, platform=platform, emulator=emulator, bundle=bundle, aot=aot,
                     uglify=uglify, hmr=hmr, release=release, snapshot=snapshot, device=device_id)

    # Check logs
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.UNKNOWN, bundle=bundle,
                                   release=release, hmr=hmr, instrumented=instrumented, app_type=AppType.NG,
                                   device=device, snapshot=snapshot)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=300)

    # Verify it looks properly
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text, timeout=180)
    device.wait_for_main_color(color=Colors.WHITE)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)
    return result


def sync_hello_world_ng(app_name, platform, device, bundle=True, uglify=False, aot=False, hmr=True,
                        instrumented=True):
    result = run_hello_world_ng(app_name=app_name, platform=platform, device=device, uglify=uglify, aot=aot, hmr=hmr)

    # Verify that application is not restarted on file changes when hmr=true
    if hmr and Settings.HOST_OS != OSType.WINDOWS:
        not_existing_string_list = ['Restarting application']
    else:
        not_existing_string_list = None

    # Apply changes
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='item.service.ts', hmr=hmr, instrumented=instrumented, app_type=AppType.NG,
                                   device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180,
                         not_existing_string_list=not_existing_string_list)

    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
    if platform == Platform.IOS:
        for number in ["10", "11"]:
            device.wait_for_text(text=number)
    else:
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='items.component.html', hmr=hmr, instrumented=instrumented,
                                   app_type=AppType.NG, aot=aot, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180,
                         not_existing_string_list=not_existing_string_list)

    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
    if platform == Platform.IOS:
        for number in ["10", "1"]:
            device.wait_for_text(text=number)
    else:
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='app.css', hmr=hmr, instrumented=instrumented, app_type=AppType.NG,
                                   device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180,
                         not_existing_string_list=not_existing_string_list)
    assert Wait.until(lambda: device.get_pixels_by_color(color=Changes.NGHelloWorld.CSS.new_color) > 100), \
        'CSS on root level not applied!'
    Log.info('CSS on root level applied successfully!')

    # Revert changes
    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='items.component.html', hmr=hmr, instrumented=instrumented,
                                   app_type=AppType.NG, aot=aot, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180,
                         not_existing_string_list=not_existing_string_list)

    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='item.service.ts', hmr=hmr, instrumented=instrumented, app_type=AppType.NG,
                                   device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180,
                         not_existing_string_list=not_existing_string_list)

    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='app.css', hmr=hmr, instrumented=instrumented, app_type=AppType.NG,
                                   device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180,
                         not_existing_string_list=not_existing_string_list)
    assert Wait.until(lambda: device.get_pixels_by_color(color=Changes.NGHelloWorld.CSS.new_color) < 100), \
        'CSS on root level not applied!'
    Log.info('CSS on root level applied successfully!')

    # Assert final and initial states are same
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)


def preview_hello_world_ng(app_name, device, bundle=False, hmr=False, instrumented=False,
                           click_open_alert=False):
    result = Preview.run_app(app_name=app_name, bundle=bundle, hmr=hmr, device=device,
                             instrumented=instrumented, click_open_alert=click_open_alert)

    # Verify app looks properly
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)
    device.wait_for_main_color(color=Colors.WHITE)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)
    return result


def preview_sync_hello_world_ng(app_name, platform, device, bundle=True, hmr=True, instrumented=False,
                                click_open_alert=False):
    result = preview_hello_world_ng(app_name=app_name, device=device, bundle=bundle, hmr=hmr,
                                    instrumented=instrumented, click_open_alert=click_open_alert)

    # Verify that application is not restarted on file changes when hmr=true
    if hmr and Settings.HOST_OS != OSType.WINDOWS:
        not_existing_string_list = ['Restarting application']
    else:
        not_existing_string_list = None

    # due to implementation when app restarts and if changes are made too quickly device is stated as
    # not connected during the restart. Workaround is to wait some seconds before next change
    time.sleep(5)

    # Edit TS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
    strings = TnsLogs.preview_file_changed_messages(run_type=RunType.INCREMENTAL, bundle=bundle,
                                                    file_name='item.service.ts', hmr=hmr, instrumented=instrumented,
                                                    device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180,
                         not_existing_string_list=not_existing_string_list)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.new_text)
    # due to implementation when no hmr app restarts and if changes are made too quickly device is stated as
    # not connected during the restart. Workaround is to wait some seconds before next change when in no hmr situation
    if not hmr:
        time.sleep(5)

    # Edit HTML file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
    strings = TnsLogs.preview_file_changed_messages(bundle=bundle, file_name='items.component.html',
                                                    hmr=hmr, instrumented=instrumented, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180,
                         not_existing_string_list=not_existing_string_list)
    if platform == Platform.IOS:
        for number in ["10", "1"]:
            device.wait_for_text(text=number)
    else:
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)
    # due to implementation when no hmr app restarts and if changes are made too quickly device is stated as
    # not connected during the restart. Workaround is to wait some seconds before next change when in no hmr situation
    if not hmr:
        time.sleep(5)

    # Edit CSS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
    strings = TnsLogs.preview_file_changed_messages(bundle=bundle, file_name='app.css',
                                                    hmr=hmr, instrumented=instrumented, device=device)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180,
                         not_existing_string_list=not_existing_string_list)
    device.wait_for_main_color(color=Changes.NGHelloWorld.CSS.new_color)
    if platform == Platform.IOS:
        for number in ["10", "1"]:
            device.wait_for_text(text=number)
    else:
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)
