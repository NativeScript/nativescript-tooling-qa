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


# noinspection PyMethodMayBeStatic,PyUnresolvedReferences
class ImageUtilsTests(unittest.TestCase):
    app_image = os.path.join(Settings.TEST_RUN_HOME, 'core_tests', 'app.png')
    iphone_image = os.path.join(Settings.TEST_RUN_HOME, 'core_tests', 'screenshot.png')
    blue = numpy.array([255, 188, 48])
    white = numpy.array([255, 255, 255])

    def test_01_read_image(self):
        img = ImageUtils.read_image(self.app_image)
        assert (img[1, 1] == numpy.array([117, 117, 117])).all(), 'Pixel 1x1 should be gray.'
        assert (img[200, 200] == numpy.array([255, 255, 255])).all(), 'Pixel 200x200 should be white.'

    def test_02_get_pixels_by_color(self):
        blue_pixels = ImageUtils.get_pixels_by_color(image_path=self.app_image, color=self.blue)
        assert blue_pixels == 18604, 'Blue pixels count is wrong. Actual: {0} Expected: {1}'.format(blue_pixels, 18604)

    def test_03_get_main_color(self):
        actual_color = ImageUtils.get_main_color(image_path=self.app_image)
        assert (actual_color == self.white).all(), 'Main color is wrong. It should be white.'

    @unittest.skip('Skip due to tesseract not installed on Travis CI.')
    def test_04_get_text(self):
        # OCR on Hello-World app
        text = ImageUtils.get_text(self.app_image)
        assert 'My App' in text
        assert 'Tap the button' in text
        assert 'TAP' in text
        assert '42 taps left' in text

        # OCR on complex screen (iPhone home screen).
        text = ImageUtils.get_text(self.iphone_image)
        assert 'Monday' in text
        assert 'Reminders' in text
        assert 'Settings' in text


if __name__ == '__main__':
    unittest.main()
