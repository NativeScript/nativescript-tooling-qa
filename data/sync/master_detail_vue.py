"""
Sync changes on JS/TS project helper.
"""
import os

from selenium.webdriver.common.by import By

from core.enums.app_type import AppType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.appium.appium_driver import AppiumDriver
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs
from products.nativescript.tns_paths import TnsPaths


def sync_master_detail_vue(app_name, platform, device, bundle=True, hmr=True):
    # Execute tns command
    result = Tns.run(app_name=app_name, platform=platform, emulator=True, wait=False, bundle=bundle, hmr=hmr)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.FULL, bundle=bundle,
                                   hmr=hmr, app_type=AppType.VUE, transfer_all=True)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=360)

    # start appium driver (need it on iOS only)
    appium = None
    if platform == Platform.IOS:
        appium = AppiumDriver(platform=platform, device=device, bundle_id=TnsPaths.get_bundle_id(app_name))

    # Verify app home page looks properly
    device.wait_for_text(text="Ford KA")
    device.wait_for_text(text=Changes.MasterDetailVUE.VUE_TEMPLATE.old_text)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)

    # Verify that application is not restarted on file changes when hmr=true
    if hmr and Settings.HOST_OS != OSType.WINDOWS:
        not_existing_string_list = ['Restarting application']
    else:
        not_existing_string_list = None

    # Edit template in .vue file
    Sync.replace(app_name=app_name, change_set=Changes.MasterDetailVUE.VUE_TEMPLATE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                   bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='CarList.vue')
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                         not_existing_string_list=not_existing_string_list)
    device.wait_for_text(text=Changes.MasterDetailVUE.VUE_TEMPLATE.new_text)

    # Edit styling in .vue file
    Sync.replace(app_name=app_name, change_set=Changes.MasterDetailVUE.VUE_STYLE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                   bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='CarList.vue')
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                         not_existing_string_list=not_existing_string_list)
    style_applied = Wait.until(lambda: device.get_pixels_by_color(Colors.RED_DARK) > 200)
    assert style_applied, 'Failed to sync changes in style.'

    # Revert styling in .vue file
    Sync.revert(app_name=app_name, change_set=Changes.MasterDetailVUE.VUE_STYLE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                   bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='CarList.vue')
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                         not_existing_string_list=not_existing_string_list)
    style_applied = Wait.until(lambda: device.get_pixels_by_color(Colors.WHITE) > 200)
    assert style_applied, 'Failed to sync changes in style.'

    device.wait_for_text(text="Ford KA")
    if platform == Platform.IOS:
        app_element = appium.driver.find_element(By.ID, "Ford KA")
        app_element.click()
    else:
        device.click(text="Ford KA")
    device.wait_for_text(text="Edit")
    device.wait_for_text(text="Price")
    Sync.replace(app_name=app_name, change_set=Changes.MasterDetailVUE.VUE_DETAIL_PAGE_TEMPLATE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                   bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='CarDetails.vue')
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings,
                         not_existing_string_list=not_existing_string_list)
    device.wait_for_text(text=Changes.MasterDetailVUE.VUE_DETAIL_PAGE_TEMPLATE.new_text)

    # Kill Appium
    if appium is not None:
        appium.stop()
