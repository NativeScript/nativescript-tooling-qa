"""
Sync changes on NG project helper.
"""

import os

from core.settings import Settings
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.tns import Tns


def sync_hello_world_ng(app_name, platform, device, bundle=False, uglify=False, aot=False):
    Tns.run(app_name=app_name, platform=platform, emulator=True, wait=False, bundle=bundle, aot=aot, uglify=uglify)
    # Verify it looks properly
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text, timeout=300, retry_delay=5)
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
