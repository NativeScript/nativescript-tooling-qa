"""
Sync changes on JS/TS project helper.
"""
import os

from core.enums.app_type import AppType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.settings.Settings import AppiumCaps
from core.utils.appium_python import AppiumDriver
from core.utils.file_utils import File
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
                                   hmr=hmr, app_type=AppType.VUE)
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=240)
    if platform == Platform.IOS:
        sync_message = 'Successfully transferred all files on device'
        content = File.read(path=result.log_file)
        assert sync_message in content

    # start appium driver
    appium = None
    if platform == Platform.IOS:
        capabilities = AppiumCaps.SIM_iOS12
        capabilities.bundleId = TnsPaths.get_bundle_id(app_name)
        capabilities.deviceName = device.name
        caps = capabilities.__dict__
        appium = AppiumDriver(caps)

    # Verify app home page looks properly
    device.wait_for_text(text="Ford KA")
    device.wait_for_text(text=Changes.MasterDetailVUE.VUE_TEMPLATE.old_text)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)

    # Edit template in .vue file
    Sync.replace(app_name=app_name, change_set=Changes.MasterDetailVUE.VUE_TEMPLATE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                   bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='CarList.vue')
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    device.wait_for_text(text=Changes.MasterDetailVUE.VUE_TEMPLATE.new_text)

    # Edit styling in .vue file
    Sync.replace(app_name=app_name, change_set=Changes.MasterDetailVUE.VUE_STYLE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                   bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='CarList.vue')
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    style_applied = Wait.until(lambda: device.get_pixels_by_color(Colors.RED_DARK) > 200)
    assert style_applied, 'Failed to sync changes in style.'

    # Revert styling in .vue file
    Sync.revert(app_name=app_name, change_set=Changes.MasterDetailVUE.VUE_STYLE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                   bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='CarList.vue')
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    style_applied = Wait.until(lambda: device.get_pixels_by_color(Colors.WHITE) > 200)
    assert style_applied, 'Failed to sync changes in style.'

    # app_element = appium.driver.find_element_by_xpath('//XCUIElementTypeStaticText[@name="Ford KA"]')
    device.wait_for_text(text="Ford KA")
    if platform == Platform.IOS:
        app_element = appium.driver.find_element_by_name("Ford KA")
        app_element.click()
    else:
        device.click(text="Ford KA")
    device.wait_for_text(text="Edit")
    device.wait_for_text(text="Price")
    Sync.replace(app_name=app_name, change_set=Changes.MasterDetailVUE.VUE_DETAIL_PAGE_TEMPLATE)
    strings = TnsLogs.run_messages(app_name=app_name, platform=platform, run_type=RunType.INCREMENTAL,
                                   bundle=bundle, hmr=hmr, app_type=AppType.VUE, file_name='CarDetails.vue')
    TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
    device.wait_for_text(text=Changes.MasterDetailVUE.VUE_DETAIL_PAGE_TEMPLATE.new_text)
    if appium is not None:
        appium.driver.quit()
