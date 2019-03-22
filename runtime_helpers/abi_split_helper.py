"""
Helper for ABI Split.
"""

from core.utils.device.device import Device, Adb


class AbiSplitHelper(object):

    @staticmethod
    def assert_apk(apk, device, app_id, image):
        Adb.install(apk,
                    device.id)
        Adb.start_application(device.id, app_id)
        Device.screen_match(device, expected_image=image, timeout=90, tolerance=1)
        Adb.stop_application(device_id=device.id, app_id=app_id)
        Adb.uninstall(app_id, device.id)
