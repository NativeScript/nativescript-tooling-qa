# coding=utf-8
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

from core.log.log import Log
from core.utils.image_utils import ImageUtils


# noinspection PyMethodMayBeStatic,PyUnresolvedReferences
class ImageUtilsTests(unittest.TestCase):
    current_folder = os.path.dirname(os.path.realpath(__file__))

    app_image = os.path.join(current_folder, 'resources', 'app.png')
    app_image_ng = os.path.join(current_folder, 'resources', 'app_ng.png')
    app_image_ios = os.path.join(current_folder, 'resources', 'app_ios.png')
    app_image_default_ios = os.path.join(current_folder, 'resources', 'app_ios_default.png')
    iphone_image = os.path.join(current_folder, 'resources', 'screenshot.png')
    unicode_image = os.path.join(current_folder, 'resources', 'unicode.png')
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

    @unittest.skipIf(os.environ.get('TRAVIS', None) is not None, 'Skip on Travis.')
    def test_04_get_text(self):
        # OCR on iOS 13
        text = ImageUtils.get_text(self.app_image_default_ios)
        assert 'taps left' in text
        assert 'Tap the button' in text
        assert 'TAP' in text
        
        # OCR on Hello-World app
        text = ImageUtils.get_text(self.app_image_ios)
        assert 'My App' in text
        assert 'Tap the button' in text
        assert 'HIT' in text
        assert '42 clicks left' in text

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

    @unittest.skipIf(os.environ.get('TRAVIS', None) is not None, 'Skip on Travis.')
    def test_05_get_text_unicode(self):
        text = ImageUtils.get_text(self.unicode_image)
        Log.info(text)
        assert 'Ter Stegen' in text
        assert 'Neymar' in text

        text = ImageUtils.get_text(self.app_image_ng)
        Log.info(text)
        assert 'Ter Stegen' in text
        assert 'Piqué' in text


if __name__ == '__main__':
    unittest.main()
