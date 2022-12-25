# TODO Scraping data from Contabilizei - Monthly

import logging
# https://stackoverflow.com/questions/45323271/how-to-run-selenium-with-chrome-in-docker
# For Docker, when I use inside AirFlow

import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from lazyutils.config.Configuration import ConfigFromEnv
from lazyutils.persistance.IPersistance import PersistanceFactory, PersistanceLayer
from lazyutils.secrets.ISecrets import SecretsFactory, Secrets
from lazyutils.structure.Callable import Callable

from walletflow.dags.webscraping.Webscrapper import Webscrapper


class Contabilizei(Callable):
    site = "https://sso.contabilizei.com/login"

    def fatura(self):
        f = c.driver.find_element(By.XPATH, "//a[text()='Ver detalhes da fatura']")
        f.click()
        time.sleep(3)
        logging.info("Going to invoice list")

        # TODO Download invoice when found

    def monthly_payment(self):

        self.wait.until(ec.visibility_of_element_located((By.XPATH, "//a[text()='Ver impostos']")))

        g = self.driver.find_element(By.XPATH, "//a[text()='Ver impostos']")
        g.click()
        self.wait.until(ec.visibility_of_element_located((By.XPATH, "//span[text()=' BAIXAR GUIA ']")))

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

    def run(self):
        self.home()
        self.login()
        # self.fatura()
        # self.home()
        self.monthly_payment()

    def __init__(self):
        self.config = ConfigFromEnv()  # Initialize logging handler also
        self.secrets = SecretsFactory(Secrets.LOCAL)

        self.driver = Webscrapper().driver
        self.wait = WebDriverWait(self.driver, 2)


if __name__ == '__main__':
    c = Contabilizei()
    c.run()
    logging.info("Finished download invoices from Contabilizei")
