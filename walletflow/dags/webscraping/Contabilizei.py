# TODO Scraping data from Contabilizei - Monthly
# TODO Scraping data from Contabilizei - Darf
import logging
# https://stackoverflow.com/questions/45323271/how-to-run-selenium-with-chrome-in-docker
# For Docker, when I use inside AirFlow

import os
from os.path import join
import time

from selenium import webdriver

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from lazyutils.config.Configuration import ConfigFromEnv
from lazyutils.persistance.IPersistance import PersistanceFactory, PersistanceLayer
from lazyutils.secrets.ISecrets import SecretsFactory, Secrets
from lazyutils.structure.Callable import Callable


class Contabilizei(Callable):
    site = "https://sso.contabilizei.com/login"
    site_map = {}

    def fatura(self):
        f = c.driver.find_element(By.XPATH, "//a[text()='Ver detalhes da fatura']")
        f.click()
        time.sleep(3)
        logging.info("Going to invoice list")

        # TODO Download invoice when found

    def monthly_payment(self):

        wait = WebDriverWait(self.driver, 10)
        wait.until(ec.visibility_of_element_located((By.XPATH, "//a[text()='Ver impostos']")))

        g = self.driver.find_element(By.XPATH, "//a[text()='Ver impostos']")
        g.click()
        time.sleep(3)
        logging.info("Going to taxes list")
        self.driver.find_element(By.XPATH, "//span[text()=' BAIXAR GUIA ']").click()

    def login(self):
        try:
            self.driver.find_element(By.ID, "user").send_keys(self.secrets.contabilizei['user'])
            self.driver.find_element(By.ID, "password").send_keys(self.secrets.contabilizei['password'])
            self.driver.find_element(By.ID, "form-login").submit()
        except NoSuchElementException:
            logging.info("Already logged in")

    def home(self):
        logging.debug("Starting Contabilizei Home")
        self.driver.delete_all_cookies()
        self.driver.get(self.site)
        logging.info("Loaded Contabilizei Home")
        wait = WebDriverWait(self.driver, 10)
        wait.until(ec.visibility_of_element_located((By.ID, "form-login")))

        time.sleep(6)

    def run(self):
        self.home()
        self.login()
        # self.fatura()
        # self.home()
        self.monthly_payment()

    def __init__(self):
        self.config = ConfigFromEnv()  # Initialize logging handler also
        self.secrets = SecretsFactory(Secrets.LOCAL)

        download_folder = self.config['Webscrapping']['invoices_folder']
        logging.info(f"Download folder: {download_folder}")

        self.driver_path = join(os.getcwd(), "chromedriver_win32", "chromedriver.exe")
        # self.driver = webdriver.Chrome(executable_path=self.driver_path)
        options = Options()
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

        self.driver = webdriver.Chrome(executable_path="chromedriver_win32\\chromedriver.exe", options=options)
        self.driver.set_page_load_timeout(15)
        self.driver.implicitly_wait(20)

        # TODO Create folder if doesn't exists

    def __del__(self):
        if self.driver:
            self.driver.quit()


if __name__ == '__main__':
    c = Contabilizei()
    c.run()
    print("finished")
