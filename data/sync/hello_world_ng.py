"""
Sync changes on NG project helper.
"""

import os

from core.enums.app_type import AppType
from core.enums.device_type import DeviceType
from core.enums.platform_type import Platform
from core.settings import Settings
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.preview_helpers import Preview
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


def run_hello_world_ng(app_name,
                       platform,
                       device,
                       bundle=True,
                       uglify=False,
                       aot=False,
                       hmr=True,
                       instrumented=True,
                       release=False,
                       snapshot=False):
    # Define if it should be executed on device or emulator
    emulator = True
    device_id = None
    if device.type == DeviceType.ANDROID or device.type == DeviceType.IOS:
        emulator = False
        device_id = device.id

    # Execute tns run command
    result = Tns.run(
        app_name=app_name,
        platform=platform,
        emulator=emulator,
        bundle=bundle,
        aot=aot,
        uglify=uglify,
        hmr=hmr,
        release=release,
        snapshot=snapshot,
        device=device_id)

    # Check logs
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.UNKNOWN,
        bundle=bundle,
        release=release,
        hmr=hmr,
        instrumented=instrumented,
        app_type=AppType.NG,
        device=device,
        snapshot=snapshot)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=300)

    # Verify it looks properly
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text, timeout=180)
    device.wait_for_main_color(color=Colors.WHITE)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name,
                                 'initial_state.png')
    device.get_screen(path=initial_state)
    return result


def sync_hello_world_ng(app_name,
                        platform,
                        device,
                        bundle=True,
                        uglify=False,
                        aot=False,
                        hmr=True,
                        instrumented=True):
    result = run_hello_world_ng(
        app_name=app_name,
        platform=platform,
        device=device,
        uglify=uglify,
        aot=aot,
        hmr=hmr)

    # Apply changes
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        file_name='item.service.ts',
        hmr=hmr,
        instrumented=instrumented,
        app_type=AppType.NG,
        device=device)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=180)

    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
    if platform == Platform.IOS:
        for number in ["10", "11"]:
            device.wait_for_text(text=number)
    else:
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        file_name='items.component.html',
        hmr=hmr,
        instrumented=instrumented,
        app_type=AppType.NG,
        aot=aot,
        device=device)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=180)

    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
    device.wait_for_main_color(color=Colors.DARK)
    if platform == Platform.IOS:
        for number in ["10", "1"]:
            device.wait_for_text(text=number)
    else:
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        file_name='app.css',
        hmr=hmr,
        instrumented=instrumented,
        app_type=AppType.NG,
        device=device)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=180)

    # Revert changes
    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        file_name='items.component.html',
        hmr=hmr,
        instrumented=instrumented,
        app_type=AppType.NG,
        aot=aot,
        device=device)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=180)

    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)
    device.wait_for_main_color(color=Colors.DARK)
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        file_name='item.service.ts',
        hmr=hmr,
        instrumented=instrumented,
        app_type=AppType.NG,
        device=device)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=180)

    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
    device.wait_for_main_color(color=Colors.WHITE)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)
    strings = TnsLogs.run_messages(
        app_name=app_name,
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        file_name='app.css',
        hmr=hmr,
        instrumented=instrumented,
        app_type=AppType.NG,
        device=device)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=180)

    # Assert final and initial states are same
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name,
                                 'initial_state.png')
    device.screen_match(
        expected_image=initial_state, tolerance=1.0, timeout=30)


def preview_hello_world_ng(app_name,
                           platform,
                           device,
                           bundle=False,
                           hmr=False,
                           instrumented=False,
                           click_open_alert=False):
    result = Preview.run_app(
        app_name=app_name,
        bundle=bundle,
        hmr=hmr,
        platform=platform,
        device=device,
        instrumented=instrumented,
        click_open_alert=click_open_alert)

    # Verify app looks properly
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)
    device.wait_for_main_color(color=Colors.WHITE)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name,
                                 'initial_state.png')
    device.get_screen(path=initial_state)
    return result


def preview_sync_hello_world_ng(app_name,
                                platform,
                                device,
                                bundle=True,
                                hmr=True,
                                instrumented=False,
                                click_open_alert=False):
    result = preview_hello_world_ng(
        app_name=app_name,
        platform=platform,
        device=device,
        bundle=bundle,
        hmr=hmr,
        instrumented=instrumented,
        click_open_alert=click_open_alert)

    # Edit TS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
    strings = TnsLogs.preview_file_changed_messages(
        platform=platform,
        run_type=RunType.INCREMENTAL,
        bundle=bundle,
        file_name='item.service.ts',
        hmr=hmr,
        instrumented=instrumented)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=180)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.new_text)

    # Edit HTML file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
    strings = TnsLogs.preview_file_changed_messages(
        platform=platform,
        bundle=bundle,
        file_name='items.component.html',
        hmr=hmr,
        instrumented=instrumented)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=180)
    if platform == Platform.IOS:
        for number in ["10", "1"]:
            device.wait_for_text(text=number)
    else:
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)

    # Edit CSS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
    strings = TnsLogs.preview_file_changed_messages(
        platform=platform,
        bundle=bundle,
        file_name='app.css',
        hmr=hmr,
        instrumented=instrumented)
    TnsLogs.wait_for_log(
        log_file=result.log_file, string_list=strings, timeout=180)
    device.wait_for_main_color(color=Colors.DARK)
    if platform == Platform.IOS:
        for number in ["10", "1"]:
            device.wait_for_text(text=number)
    else:
        for number in ["8", "9"]:
            device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)
