import numpy


class Colors(object):
    """
    Notes: OpenCV color order is:
    0 - blue
    1 - green
    2 - red
    """
    WHITE = numpy.array([255, 255, 255])  # White color
    DARK = numpy.array([48, 48, 48])  # Dark of default theme (on NG hello-world app).
    LIGHT_BLUE = numpy.array([255, 188, 48])  # Blue of TAP button on hello-world app.
    ACCENT_DARK = numpy.array([255, 83, 58])  # Dark blue in pro templates.
    PINK = numpy.array([203, 192, 255])  # Pink (standard CSS color).
    RED = numpy.array([0, 0, 255])  # Red (standard CSS color).
    RED_DARK = numpy.array([5, 4, 229])  # A bit custom red (happens when apply red on master-detail template).
    PURPLE = numpy.array([128, 0, 128])  # Purple (standard CSS color).
    YELLOW = numpy.array([0, 255, 255])  # Yellow (standard CSS color).
    YELLOW_ICON = numpy.array([0, 242, 255])  # Yellow of star.png
    GREEN_ICON = numpy.array([0, 128, 0])  # Green of background colour of resources generate images
