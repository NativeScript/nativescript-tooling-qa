"""
Helper for ABI Split.
"""

from core.utils.device.device import Device, Adb


class AbiSplitHelper(object):
    @staticmethod
    def assert_apk(apk, device, app_id):
        Adb.install(apk, device.id)
        Adb.start_application(device.id, app_id)
        Device.wait_for_text(device, text='Ter Stegen', timeout=90)
        Adb.stop_application(device_id=device.id, app_id=app_id)
        Adb.uninstall(app_id, device.id)
