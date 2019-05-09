# pylint: disable=import-error
# pylint: disable=broad-except
# pylint: disable=too-many-nested-blocks
import atomac


# noinspection PyBroadException
class SimAuto(object):

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
                    window.activate()
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
