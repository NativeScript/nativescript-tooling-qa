"""
Image utils.

Notes: OpenCV color order is:
0 - blue
1 - green
2 - red
"""

import cv2
import numpy
from PIL import Image


class ImageUtils(object):
    @staticmethod
    def image_match(actual_image, expected_image, tolerance=0.05):
        """
        Compare two images.
        :param actual_image: Path to actual image.
        :param expected_image: Path to expected image.
        :param tolerance: Tolerance in percents.
        :return: match (boolean value), diff_percent (diff %), diff_image (diff image)
        """
        actual_image = Image.open(actual_image)
        actual_pixels = actual_image.load()
        expected_image = Image.open(expected_image)
        expected_pixels = expected_image.load()
        width, height = expected_image.size

        total_pixels = width * height
        diff_pixels = 0
        match = False
        diff_image = actual_image.copy()
        for x in range(0, width):
            for y in range(40, height):
                actual_pixel = actual_pixels[x, y]
                expected_pixel = expected_pixels[x, y]
                if actual_pixel != expected_pixel:
                    actual_r = actual_pixel[0]
                    actual_g = actual_pixel[1]
                    actual_b = actual_pixel[2]
                    expected_r = expected_pixel[0]
                    expected_g = expected_pixel[1]
                    expected_b = expected_pixel[2]
                    if abs(actual_r + actual_g + actual_b - expected_r - expected_g - expected_b) > 30:
                        diff_pixels += 1
                        diff_image.load()[x, y] = (255, 0, 0)

        diff_percent = 100 * float(diff_pixels) / total_pixels
        if diff_percent < tolerance:
            match = True

        return match, diff_percent, diff_image

    @staticmethod
    def read_image(image_path):
        """
        Load image from file to opencv object.
        :param image_path: Image path.
        :return: Image as opencv object.
        """
        return cv2.imread(image_path)

    @staticmethod
    def get_pixels_by_color(image_path, color, rdb_tolerance=25):
        """
        Get count of pixels of specific color.
        :param image_path: Image path.
        :param color: Color as numpy array. Example: numpy.array([255, 217, 141])
        :param rdb_tolerance If diff of sums of rgb values is less then specified count pixels will be counted as equal.
        :return: Count of pixels.
        """
        img = ImageUtils.read_image(image_path=image_path)
        colors, counts = numpy.unique(img.reshape(-1, 3), axis=0, return_counts=True)
        max_count = 0
        for n_color, count in zip(colors, counts):
            # noinspection PyUnresolvedReferences
            b_diff = abs(n_color[0] - color[0])
            g_diff = abs(n_color[1] - color[1])
            r_diff = abs(n_color[2] - color[2])
            if b_diff < rdb_tolerance and g_diff < rdb_tolerance and r_diff < rdb_tolerance:
                if count > max_count:
                    max_count = count
        return max_count

    @staticmethod
    def get_main_color(image_path):
        img = ImageUtils.read_image(image_path=image_path)
        colors, counts = numpy.unique(img.reshape(-1, 3), axis=0, return_counts=True)
        max_count = 0
        main_color = None
        for color, count in zip(colors, counts):
            if count > max_count:
                max_count = count
                main_color = color
        return main_color
