# pylint: disable=redefined-builtin
import logging
import os
import time

from core.enums.device_type import DeviceType
from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.idevice import IDevice
from core.utils.device.simctl import Simctl
from core.utils.file_utils import File, Folder
from core.utils.image_utils import ImageUtils
from core.utils.run import run
from core.utils.wait import Wait

if Settings.HOST_OS is OSType.OSX:
    from core.utils.device.simauto import SimAuto


class Device(object):
    # noinspection PyShadowingBuiltins
    def __init__(self, id, name, type, version):
        self.id = id
        self.type = type
        self.version = version

        if type is DeviceType.IOS:
            type = run(cmd="ideviceinfo | grep ProductType").output
            type = type.replace(',', '')
            type = type.replace('ProductType:', '').strip(' ')
            self.name = type
        else:
            self.name = name

    def are_texts_visible(self, texts):
        is_list = isinstance(texts, list)
        if is_list:
            all_texts_visible = True
            for text in texts:
                is_visible = self.is_text_visible(text)
                if is_visible is False:
                    all_texts_visible = False
                    break
            return all_texts_visible
        else:
            raise Exception('are_texts_visible needs array as texts param.')

    def is_text_visible(self, text):
        is_visible = False
        if self.type is DeviceType.EMU or self.type is DeviceType.ANDROID:
            is_visible = Adb.is_text_visible(device_id=self.id, text=text)
        if self.type is DeviceType.SIM:
            is_visible = SimAuto.is_text_visible(self, text)
        if self.type is DeviceType.IOS:
            is_visible = IDevice.is_text_visible(device_id=self.id, text=text)

        # Retry find with ORC (only for IOS, for example if macOS automation fails)
        if not is_visible and (self.type is DeviceType.SIM or self.type is DeviceType.IOS):
            actual_text = self.get_text()
            if text in actual_text:
                is_visible = True
            else:
                Log.debug('Current text on {0}: {1}{2}'.format(self.id, os.linesep, actual_text))

        return is_visible

    def get_text(self):
        img_name = "actual_{0}_{1}.png".format(self.id, time.time())
        actual_image_path = os.path.join(Settings.TEST_OUT_IMAGES, img_name)
        File.delete(actual_image_path)
        self.get_screen(path=actual_image_path, log_level=logging.DEBUG)
        return ImageUtils.get_text(image_path=actual_image_path)

    def wait_for_text(self, text, timeout=60, retry_delay=1):
        t_end = time.time() + timeout
        found = False
        error_msg = '{0} NOT found on {1}.'.format(text, self.name)
        found_msg = '{0} found on {1}.'.format(text, self.name)
        while time.time() < t_end:
            if self.is_text_visible(text=text):
                found = True
                Log.info(found_msg)
                break
            else:
                Log.info(error_msg + ' Waiting ...')
                time.sleep(retry_delay)
        if not found:
            text = self.get_text()
            Log.info('Current text: {0}{1}'.format(os.linesep, text))
        assert found, error_msg

    def get_screen(self, path, log_level=logging.INFO):
        """
        Save screen of mobile device.
        :param path: Path to image that will be saved.
        :param log_level: Log level.
        """

        # Ensure folder to save the screen exists
        File.delete(path)
        Folder.create(folder=os.path.dirname(path))

        if self.type is DeviceType.EMU or self.type is DeviceType.ANDROID:
            Adb.get_screen(device_id=self.id, file_path=path)
        if self.type is DeviceType.SIM:
            Simctl.get_screen(sim_id=self.id, file_path=path)
        if self.type is DeviceType.IOS:
            IDevice.get_screen(device_id=self.id, file_path=path)

        image_saved = False
        if File.exists(path):
            size = os.path.getsize(path)
            if size > 10:
                image_saved = True
        if image_saved:
            message = "Image of {0} saved at {1}".format(self.id, path)
            Log.log(level=log_level, msg=message)
        else:
            message = "Failed to save image of {0} saved at {1}".format(self.id, path)
            Log.error(message)
            raise Exception(message)

    def screen_match(self, expected_image, tolerance=0.1, timeout=30):
        """
        Verify screen match expected image.
        :param expected_image: Name of expected image.
        :param tolerance: Tolerance in percents.
        :param timeout: Timeout in seconds.
        """

        if File.exists(expected_image):
            match = False
            error_msg = 'Screen of {0} does NOT match {1}.'.format(self.name, expected_image)
            t_end = time.time() + timeout
            diff_image = None
            while time.time() < t_end:
                actual_image = expected_image.replace('.png', '_actual.png')
                self.get_screen(path=actual_image, log_level=logging.DEBUG)
                result = ImageUtils.image_match(actual_image=actual_image,
                                                expected_image=expected_image,
                                                tolerance=tolerance)
                if result[0]:
                    Log.info('Screen of {0} matches {1}.'.format(self.name, expected_image))
                    match = True
                    break
                else:
                    diff_image = result[2]
                    error_msg += ' Diff is {0} %.'.format(result[1])
                    Log.info(error_msg)
                    time.sleep(3)
            if not match:
                if diff_image is not None:
                    diff_image_path = expected_image.replace('.png', '_diff.png')
                    diff_image.save(diff_image_path)
            assert match, error_msg
        else:
            Log.info('Expected image not found!')
            Log.info('Actual image will be saved as expected: ' + expected_image)
            time.sleep(timeout)
            self.get_screen(path=expected_image, log_level=logging.DEBUG)
            assert False, "Expected image not found!"

    def get_pixels_by_color(self, color):
        image_path = os.path.join(Settings.TEST_OUT_IMAGES, self.name,
                                  'screen_{0}.png'.format(int(time.time() * 1000)))
        self.get_screen(image_path, log_level=logging.DEBUG)
        return ImageUtils.get_pixels_by_color(image_path, color)

    # noinspection PyShadowingBuiltins
    def wait_for_color(self, color, pixel_count, delta=10, timeout=30):
        found = False
        t_end = time.time() + timeout
        err_msg = ''
        while time.time() < t_end:
            count = self.get_pixels_by_color(color=color)
            msg = '{0} pixels of type {1} found on {2}'.format(count, str(color), self.name)
            err_msg = msg + ' Expected count: {0}'.format(pixel_count)
            min_count = pixel_count - int(pixel_count * delta / 100)
            max_count = pixel_count + int(pixel_count * delta / 100)
            if min_count <= count <= max_count:
                Log.info(msg)
                found = True
                break
            else:
                Log.info(err_msg)
                time.sleep(1)
        assert found, err_msg

    def get_main_color(self):
        image_path = os.path.join(Settings.TEST_OUT_IMAGES, self.name, 'screen_{0}.png'.format(int(time.time() * 1000)))
        self.get_screen(image_path, log_level=logging.DEBUG)
        return ImageUtils.get_main_color(image_path)

    # noinspection PyUnresolvedReferences
    def wait_for_main_color(self, color, timeout=30):
        result = Wait.until(lambda: (self.get_main_color() == color).all(), timeout=timeout)
        if result:
            Log.info('Main color is: ' + str(color))
        assert result, "Expected main color: " + str(color) + os.linesep + \
                       "Actual main color: " + str(self.get_main_color())

    def click(self, text):
        if self.type is DeviceType.EMU or self.type is DeviceType.ANDROID:
            raise NotImplementedError('Click not implemented for Android devices.')
        elif self.type is DeviceType.SIM:
            SimAuto.click(self, text=text)
        else:
            raise NotImplementedError('Click not implemented for iOS devices.')
