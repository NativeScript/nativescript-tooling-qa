"""
Tests for image utils.

Notes: OpenCV color order is:
0 - blue
1 - green
2 - red
"""
import os
import unittest

import numpy

from core.settings import Settings
from core.utils.image_utils import ImageUtils


# noinspection PyMethodMayBeStatic
class ImageUtilsTests(unittest.TestCase):
    image_path = os.path.join(Settings.TEST_RUN_HOME, 'core_tests', 'app.png')
    blue = numpy.array([255, 188, 48])
    white = numpy.array([255, 255, 255])

    def test_01_read_image(self):
        img = ImageUtils.read_image(self.image_path)
        assert (img[1, 1] == numpy.array([117, 117, 117])).all(), 'Pixel 1x1 should be gray.'
        assert (img[200, 200] == numpy.array([255, 255, 255])).all(), 'Pixel 200x200 should be white.'

    def test_02_get_pixels_by_color(self):
        blue_pixels = ImageUtils.get_pixels_by_color(image_path=self.image_path, color=self.blue)
        assert blue_pixels == 18604, 'Blue pixels count is wrong. Actual: {0} Expected: {1}'.format(blue_pixels, 18604)

    def test_03_get_main_color(self):
        actual_color = ImageUtils.get_main_color(image_path=self.image_path)
        assert (actual_color == self.white).all(), 'Main color is wrong. It should be white.'


if __name__ == '__main__':
    unittest.main()
