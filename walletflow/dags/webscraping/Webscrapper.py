import os
from os.path import join
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from lazyutils.structure.Singleton import Singleton
from lazyutils.config.Configuration import ConfigFromEnv


class Webscrapper(Singleton):
    def start(self):
        download_folder = self.config['Webscrapping']['invoices_folder']
        logging.info(f"Download folder: {download_folder}")

        self.driver_path = join(os.getcwd(), "chromedriver_win32", "chromedriver.exe")
        # self.driver = webdriver.Chrome(executable_path=self.driver_path)
        options = Options()

        # TODO Change to be receive from Config File
        options.add_argument("user-data-dir=C:\\Users\\paulo\\AppData\\Local\\Google\\Chrome\\User Data - Copia")
        options.add_argument(f"download.default_directory={download_folder}")
        options.add_argument("--no-sandbox")
        options.add_argument("--log-path=chromedriver.log")
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        options.add_experimental_option("prefs", {
            "download.default_directory": download_folder,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })

        self._driver = webdriver.Chrome(executable_path="chromedriver_win32\\chromedriver.exe", options=options)
        self._driver.set_page_load_timeout(15)
        self._driver.implicitly_wait(20)

        # TODO Create download folder if doesn't exists

    @property
    def driver(self):
        if self._driver is None:
            self.start()

        return self._driver

    def __init__(self):
        self._driver = None
        self.driver_path = None
        self.config = ConfigFromEnv()  # Initialize logging handler also

    def shutdown(self):
        if self._driver:
            self.driver.quit()
            self._driver = None

    def __del__(self):
        if self._driver:
            self.driver.quit()
