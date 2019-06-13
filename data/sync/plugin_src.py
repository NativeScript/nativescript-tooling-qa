"""
Sync changes on JS/TS project helper.
"""
import datetime
import os

from core.enums.app_type import AppType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.wait import Wait
from data.changes import Changes, Sync
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs
from products.nativescript.tns_paths import TnsPaths


def sync_plugin_verify_demo(app_name, app_type, plugin_name, platform, device, bundle=True, hmr=True):
    """
    Change plugin in src and verify demo is updated.
    :param app_name: The name of the App. for example: demo, demo-angular, demo-vue
    :param app_type: Application type: js,ts,ng,vue.
    :param plugin_name: The name of the plugin. for example: nativescript-datetimepicker
    :param platform: The platform type Platform.IOS or Platform.ANDROID
    :param device: Device info.
    :param bundle: Bundle flag boolean.
    :param hmr: HMR flag boolean.
    """
    # Navigate to demo folder and run the demo app
    app_folder = 'demo'
    if app_type == AppType.NG:
        app_folder = 'demo-angular'
        app_name = app_name + 'ng'
    elif app_type == AppType.VUE:
        app_folder = 'demo-vue'
        app_name = app_name + 'vue'
    app_path = os.path.join(Settings.TEST_SUT_HOME, plugin_name, app_folder)

    result = Tns.run(app_name=app_path, platform=platform, emulator=True, wait=False, bundle=bundle, hmr=hmr)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.FULL, bundle=bundle,
                                   hmr=hmr, app_type=AppType.VUE, transfer_all=False)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=240)

    # Verify app home page looks properly
    device.wait_for_text(text="DateTimePicker Demo")
    device.wait_for_text(text="DatePickerField")
    device.wait_for_text(text="TimePickerField")
    device.wait_for_text(text="DateTimePickerFields")
    device.wait_for_text(text="Custom Buttons")
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)
    # Click DatePicker field and verify pickers are visible
    device.click(text="DatePickerField")
    device.wait_for_text("basic usage")
    device.wait_for_text("select date")
    device.wait_for_text("initial values")

    # # Edit common file in SRC
    change_set = Changes.DateTimePicker.COMMON_TS
    File.replace(path=change_set.file_path, old_string=change_set.old_value, new_string=change_set.new_value,
                 fail_safe=True)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL, bundle=bundle,
                                   hmr=hmr, app_type=AppType.VUE, transfer_all=True)

    # remove "Skipping prepare." from strings since no new build is triggered.
    strings.remove("Skipping prepare.")
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=240)
    # Click on datepicker field and verify new value of picker is applied
    device.click(text="DatePickerField")
    today = datetime.date.today().strftime("%b %d, %Y")
    device.wait_for_text(today)
