import os
from time import sleep

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.ci.jenkins import Jenkins
from core.utils.file_utils import Folder
from core.utils.process import Process


class Chrome(object):
    driver = None
    implicitly_wait = None

    def __init__(self, kill_old=True, implicitly_wait=20):
        if kill_old:
            self.kill()
        path = ChromeDriverManager().install()
        Log.info('Starting Google Chrome ...')
        profile_path = os.path.join(Settings.TEST_OUT_TEMP, 'chrome_profile')
        Folder.clean(profile_path)
        options = webdriver.ChromeOptions()
        options.add_argument('user-data-dir={0}'.format(profile_path))
        self.driver = webdriver.Chrome(executable_path=path, chrome_options=options)
        self.implicitly_wait = implicitly_wait
        self.driver.implicitly_wait(self.implicitly_wait)
        self.driver.maximize_window()
        self.focus()
        Log.info('Google Chrome started!')

    def open(self, url):
        self.driver.get(url)
        Log.info('Open url: ' + url)

    def kill(self, force=Jenkins.is_ci()):
        """
        Kill Chrome browsers instance(s).
        :param force: If false it will kill only browsers started by driver.
        If true it will force kill all chrome processes.
        By default `force` is set to false on local machines and true on CI (when JENKINS_HOME variable is set).
        """
        if self.driver is not None:
            self.driver.quit()
        if force:
            if Settings.HOST_OS == OSType.OSX:
                Process.kill(proc_name='Google Chrome', proc_cmdline=None)
            else:
                Process.kill(proc_name="chrome", proc_cmdline=None)
            Process.kill(proc_name='chromedriver')
        Log.info('Kill Chrome browser!')

    def focus(self):
        self.driver.switch_to.window(self.driver.current_window_handle)
        Log.info("Focus Chrome browser.")

    def get_absolute_center(self, element):
        self.focus()
        sleep(1)
        rel_x = element.location['x']
        rel_y = element.location['y']
        nav_panel_height = self.driver.execute_script('return window.outerHeight - window.innerHeight;')
        x = rel_x + element.size['width'] * 0.5
        y = rel_y + nav_panel_height + element.size['height'] * 0.5
        return x, y
