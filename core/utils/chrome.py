from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from log.log import Log


class Chrome(object):

    def __init__(self):
        path = ChromeDriverManager().install()
        Log.info('Starting Google Chrome ...')
        self.driver = webdriver.Chrome(executable_path=path)
        Log.info('Google Chrome started!')

    def open(self, url):
        self.driver.get(url)
        Log.info('Open url: ' + url)

    def kill(self):
        self.driver.quit()
        Log.info('Kill Chrome browser!')
