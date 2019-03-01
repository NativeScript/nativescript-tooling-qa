"""
Sync changes on JS/TS project helper.
"""
import os

from core.enums.app_type import AppType
from core.settings import Settings
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


def sync_blank_vue(app_name, platform, device, bundle=False, hmr=False, instrumented=False):
    # Execute `tns run` and wait until logs are OK
    result = Tns.run(app_name=app_name, platform=platform, emulator=True, wait=False, bundle=bundle, hmr=hmr)

    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.FULL, bundle=bundle,
                                   hmr=hmr, app_type=AppType.VUE, instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=240)

    # Verify it looks properly
    device.wait_for_text(text=Changes.BlankVue.VUE_SCRIPT.old_text)
    device.wait_for_text(text=Changes.BlankVue.VUE_TEMPLATE.old_text)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)

    # Edit script in .vue file
    Sync.replace(app_name=app_name, change_set=Changes.BlankVue.VUE_SCRIPT)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, app_type=AppType.VUE, file_name='Home.vue', instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    device.wait_for_text(text=Changes.BlankVue.VUE_SCRIPT.new_text)

    # Edit template in .vue file
    Sync.replace(app_name=app_name, change_set=Changes.BlankVue.VUE_TEMPLATE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, app_type=AppType.VUE, file_name='Home.vue', instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    device.wait_for_text(text=Changes.BlankVue.VUE_TEMPLATE.new_text)

    # Edit styling in .vue file
    Sync.replace(app_name=app_name, change_set=Changes.BlankVue.VUE_STYLE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, app_type=AppType.VUE, file_name='Home.vue', instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    style_applied = Wait.until(lambda: device.get_pixels_by_color(Colors.RED) > 100)
    assert style_applied, 'Failed to sync changes in style.'

    # Revert script in .vue file
    Sync.revert(app_name=app_name, change_set=Changes.BlankVue.VUE_SCRIPT)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, app_type=AppType.VUE, file_name='Home.vue', instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    device.wait_for_text(text=Changes.BlankVue.VUE_SCRIPT.old_text)

    # Revert template in .vue file
    Sync.revert(app_name=app_name, change_set=Changes.BlankVue.VUE_TEMPLATE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, app_type=AppType.VUE, file_name='Home.vue', instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    device.wait_for_text(text=Changes.BlankVue.VUE_TEMPLATE.old_text)

    # Revert styling in .vue file
    Sync.revert(app_name=app_name, change_set=Changes.BlankVue.VUE_STYLE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, app_type=AppType.VUE, file_name='Home.vue', instrumented=instrumented)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

    # Skip next steps because of https://github.com/nativescript-vue/nativescript-vue/issues/425
    # style_applied = Wait.until(lambda: device.get_pixels_by_color(Colors.RED) == 0)
    # assert style_applied, 'Failed to sync changes in style.'

    # Assert final and initial states are same
    device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)
