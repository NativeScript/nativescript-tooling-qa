"""
Sync changes on JS/TS project helper.
"""
import os

from core.enums.app_type import AppType
from core.log.log import Log
from core.settings import Settings
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.preview_helpers import Preview
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


def __run_vue(app_name, platform, bundle, hmr):
    # Execute `tns run` and wait until logs are OK
    return Tns.run(app_name=app_name, platform=platform, emulator=True, wait=False, bundle=bundle, hmr=hmr)


def __preview_vue(app_name, platform, device, bundle, hmr):
    # Execute `tns run` and wait until logs are OK
    return Preview.run_app(app_name=app_name, bundle=bundle, hmr=hmr, platform=platform, device=device,
                           click_open_alert=True)


def __workflow(preview, app_name, platform, device, bundle=True, hmr=True):
    # Execute tns command
    if preview:
        result = __preview_vue(app_name=app_name, platform=platform, device=device, bundle=bundle, hmr=hmr)
    else:
        result = __run_vue(app_name=app_name, platform=platform, bundle=bundle, hmr=hmr)

    if preview:
        Log.info('Skip logs checks.')
    else:
        strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.FULL, bundle=bundle,
                                       hmr=hmr, app_type=AppType.VUE)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=240)

    # Verify it looks properly
    device.wait_for_text(text=Changes.BlankVue.VUE_SCRIPT.old_text, timeout=150)
    device.wait_for_text(text=Changes.BlankVue.VUE_TEMPLATE.old_text, timeout=200)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)

    # Verify that application is not restarted on file changes when hmr=true
    if hmr:
        not_existing_string_list = ['Restarting application']
    else:
        not_existing_string_list = None

    # Edit script in .vue file
    Sync.replace(app_name=app_name, change_set=Changes.BlankVue.VUE_SCRIPT)
    if preview:
        Log.info('Skip logs checks.')
    else:
        strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                       bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='Home.vue')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_string_list)
    device.wait_for_text(text=Changes.BlankVue.VUE_SCRIPT.new_text)

    # Edit template in .vue file
    Sync.replace(app_name=app_name, change_set=Changes.BlankVue.VUE_TEMPLATE)
    if preview:
        Log.info('Skip logs checks.')
    else:
        strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                       bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='Home.vue')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_string_list)
    device.wait_for_text(text=Changes.BlankVue.VUE_TEMPLATE.new_text)

    # Edit styling in .vue file
    Sync.replace(app_name=app_name, change_set=Changes.BlankVue.VUE_STYLE)
    if preview:
        Log.info('Skip logs checks.')
    else:
        strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                       bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='Home.vue')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_string_list)
    style_applied = Wait.until(lambda: device.get_pixels_by_color(Colors.RED) > 100)
    assert style_applied, 'Failed to sync changes in style.'

    # Revert script in .vue file
    Sync.revert(app_name=app_name, change_set=Changes.BlankVue.VUE_SCRIPT)
    if preview:
        Log.info('Skip logs checks.')
    else:
        strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                       bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='Home.vue')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_string_list)
    device.wait_for_text(text=Changes.BlankVue.VUE_SCRIPT.old_text)

    # Revert template in .vue file
    Sync.revert(app_name=app_name, change_set=Changes.BlankVue.VUE_TEMPLATE)
    if preview:
        Log.info('Skip logs checks.')
    else:
        strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                       bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='Home.vue')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_string_list)
    device.wait_for_text(text=Changes.BlankVue.VUE_TEMPLATE.old_text)

    # Revert styling in .vue file
    Sync.revert(app_name=app_name, change_set=Changes.BlankVue.VUE_STYLE)
    if preview:
        Log.info('Skip logs checks.')
    else:
        strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                       bundle=bundle,
                                       hmr=hmr, app_type=AppType.VUE, file_name='Home.vue')
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                             not_existing_string_list=not_existing_string_list)

    if hmr:
        Log.info('Skip next steps because of https://github.com/nativescript-vue/nativescript-vue/issues/425')
    else:
        style_applied = Wait.until(lambda: device.get_pixels_by_color(Colors.RED) == 0)
        assert style_applied, 'Failed to sync changes in style.'

    # Assert final and initial states are same
    device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)


def sync_blank_vue(app_name, platform, device, bundle=True, hmr=True):
    __workflow(preview=False, app_name=app_name, platform=platform, device=device, bundle=bundle, hmr=hmr)


def preview_blank_vue(app_name, platform, device, bundle=True, hmr=True):
    __workflow(preview=True, app_name=app_name, platform=platform, device=device, bundle=bundle, hmr=hmr)
