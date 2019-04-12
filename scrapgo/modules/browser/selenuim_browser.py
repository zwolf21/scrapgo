import time
from pprint import pprint

from collections import namedtuple

from selenium import webdriver


class Browser(object):
    BROWSER_NAME = 'Chrome'
    WEBDRIVER = 'chromedriver.exe'
    INITIAL_URL = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        f = getattr(webdriver, self.BROWSER_NAME.capitalize())
        self.browser = f(self.WEBDRIVER)
        self.browser.get(self.INITIAL_URL)

    def find_click(xpath):
        return self.browser.find_elements_by_xpath(xpath)
