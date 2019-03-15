# pylint: disable=import-error
# pylint: disable=broad-except
# pylint: disable=too-many-nested-blocks
import atomac


# noinspection PyBroadException
import logging

from core.utils.run import run


class SimAuto(object):

    @staticmethod
    def run_simctl_command(command, parameters="", device_id=None, wait=True, timeout=60, fail_safe=False,
                           log_level=logging.DEBUG):
        if device_id is None:
            command = '{0} {1} {2} {3}'.format("xcrun simctl", command, "booted", parameters)
        else:
            command = '{0} {1} {2} {3}'.format("xcrun simctl", command, device_id, parameters)
        return run(cmd=command, wait=wait, timeout=timeout, fail_safe=fail_safe, log_level=log_level)

    @staticmethod
    def find(device_info, text):
        try:
            # Get list of iOS Simulator Windows
            simulator = atomac.getAppRefByBundleId("com.apple.iphonesimulator")
            windows = simulator.findAll(AXRole='AXWindow')
            names = list()

            # Get all simulator's windows names
            for window in windows:
                names.append(window.AXTitle)

            # Get the full name of the window where the click will be performed
            for name in names:
                if device_info.name in name:
                    window = simulator.findFirstR(AXTitle=name)
                    elements = window.findAllR()
                    for element in elements:
                        if 'AXValue' in element.getAttributes():
                            if text in str(element.AXValue):
                                return element
                            elif 'AXTitle' in element.getAttributes():
                                if text in str(element.AXTitle):
                                    return element
            return None
        except Exception:
            return None

    @staticmethod
    def is_text_visible(device_info, text):
        element = SimAuto.find(device_info=device_info, text=text)
        if element is not None:
            return True
        return False

    @staticmethod
    def click(device_info, text):
        element = SimAuto.find(device_info=device_info, text=text)
        if element is not None:
            element_position = element.AXPosition
            element_size = element.AXSize
            click_point = ((element_position[0] + element_size[0] / 2), (element_position[1] + element_size[1] / 2))
            element.clickMouseButtonLeft(click_point)
        else:
            raise Exception('Can not locate "{0}" in {1} simulator.'.format(text, device_info.name))

    @staticmethod
    def get_log_file(device_id):
        command = "spawn"
        parameters = "log stream --level=debug"
        log_file = SimAuto.run_simctl_command(command=command, device_id=device_id, parameters=parameters,
                                              wait=False).log_file
        return log_file
