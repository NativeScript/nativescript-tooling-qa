import logging
import os
import time

from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.image_utils import ImageUtils
from core.utils.run import run


class Screen(object):

    @staticmethod
    def save_screen(path, log_level=logging.DEBUG):
        """
        Save screen of host machine.
        :param path: Path where screen will be saved.
        :param log_level: Log level of the command.
        """
        Log.log(level=log_level, msg='Save current host screen at {0}'.format(path))
        if Settings.HOST_OS is OSType.LINUX:
            import os
            os.system("import -window root {0}".format(path))
        else:
            try:
                from PIL import ImageGrab
                im = ImageGrab.grab()
                im.save(path)
            except IOError:
                Log.error('Failed to take screen of host OS')
                if Settings.HOST_OS is OSType.OSX:
                    Log.info('Retry...')
                    run(cmd='screencapture ' + path)

    @staticmethod
    def get_screen_text():
        """
        Get text of current screen of host machine.
        :return: All the text visible on screen as string
        """
        actual_image_path = os.path.join(Settings.TEST_OUT_IMAGES, "host_{0}.png".format(time.time()))
        if File.exists(actual_image_path):
            File.clean(actual_image_path)
        Screen.save_screen(path=actual_image_path)
        text = ImageUtils.get_text(image_path=actual_image_path)
        File.clean(actual_image_path)
        return text

    @staticmethod
    def wait_for_text(text, timeout=60):
        """
        Wait for text to be visible screen of host machine.
        :param text: Text that should be visible on the screen.
        :param timeout: Timeout in seconds.
        :return: True if text found, False if not found.
        """
        t_end = time.time() + timeout
        found = False
        actual_text = ''
        while time.time() < t_end:
            actual_text = Screen.get_screen_text()
            if text in actual_text:
                Log.info('"{0}" found on screen.'.format(text))
                found = True
                break
            else:
                Log.debug('"{0}" NOT found on screen.'.format(text))
                time.sleep(5)
        if not found:
            Log.info('Actual text: {0}{1}'.format(os.linesep, actual_text))
        return found
