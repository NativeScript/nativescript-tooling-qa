"""
Sync changes on NG project helper.
"""

import os

from core.enums.app_type import AppType
from core.enums.platform_type import Platform
from core.settings import Settings
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


def sync_hello_world_ng(app_name, platform, device, bundle=False, uglify=False, aot=False, hmr=False,
                        instrumented=True):
    result = Tns.run(app_name=app_name, platform=platform, emulator=True, wait=False,
                     bundle=bundle, aot=aot, uglify=uglify, hmr=hmr)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, bundle=bundle,
                                   hmr=hmr, instrumented=instrumented, app_type=AppType.NG)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180)
    
    # Verify it looks properly
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text, timeout=300, retry_delay=5)
    device.wait_for_main_color(color=Colors.WHITE)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)

    # Apply changes
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='item.service.ts', hmr=hmr, instrumented=instrumented, app_type=AppType.NG)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180)

    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
    for number in ["8", "9"]:
        device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='items.component.html', hmr=hmr, instrumented=instrumented,
                                   app_type=AppType.NG)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180)

    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
    device.wait_for_main_color(color=Colors.DARK)
    for number in ["8", "9"]:
        device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='app.css', hmr=hmr, instrumented=instrumented, app_type=AppType.NG)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180)

    # Revert changes
    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.new_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='items.component.html', hmr=hmr, instrumented=instrumented,
                                   app_type=AppType.NG)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180)

    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)
    device.wait_for_main_color(color=Colors.DARK)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='item.service.ts', hmr=hmr, instrumented=instrumented, app_type=AppType.NG)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180)

    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
    device.wait_for_main_color(color=Colors.WHITE)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   file_name='app.css', hmr=hmr, instrumented=instrumented, app_type=AppType.NG)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180)

    # Assert final and initial states are same
    device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)
