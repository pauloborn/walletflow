import logging
import time

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from lazyutils.config.Configuration import ConfigFromEnv
from lazyutils.secrets.ISecrets import SecretsFactory, Secrets
from lazyutils.structure.Callable import Callable

from walletflow.dags.webscraping.Webscrapper import Webscrapper


class LiggaTelecom(Callable):
    site = "https://liggatelecom.com.br/autoatendimento/pub/login.jsf"

    def get_invoice(self):
        divextratos = self.driver.find_element(By.ID, "divListaExtratos")
        open_invoices = divextratos.find_elements(By.XPATH, "//span[text()='Aberto']/following-sibling::span/a")

        logging.debug(f"Found {len(open_invoices)} invoices in ligga telecom to download")
        retries = 3
        downloaded = False

        while not downloaded and retries > 0:
            try:
                for invoice in open_invoices:
                    invoice.click()
                    downloaded = True

            except StaleElementReferenceException:
                retries -= 1
                logging.warning("Stale error when trying to download")
                time.sleep(3)

        if retries < 1:
            logging.error("Couldn't download invoices from Ligga Telecom")

        time.sleep(2)

        logging.info("Ligga Telecom - Invoice downloaded")

    def login(self):

        user = self.driver.find_element(By.ID, "form_login_new:login")
        user.clear()
        user.send_keys(self.secrets.ligga['user'])

        p = self.driver.find_element(By.ID, "form_login_new:senha")
        p.clear()
        p.send_keys(self.secrets.ligga['password'])

        self.driver.find_element(By.ID, "form_login_new:btnLogin").click()

        self.wait.until(ec.visibility_of_element_located((By.ID, "spanUsuarioLogado")))
        self.wait.until(ec.visibility_of_element_located((By.ID, "divListaExtratos")))

        logging.info("Ligga Telecom - Logged IN")

    def home(self):
        logging.debug("Starting Ligga Home")
        self.driver.delete_all_cookies()
        self.driver.get(self.site)
        logging.info("Loaded Ligga Home")

        self.wait.until(ec.visibility_of_element_located((By.ID, "form_login_new")))
        self.wait.until(ec.visibility_of_element_located((By.ID, "form_login_new:login")))
        self.wait.until(ec.visibility_of_element_located((By.ID, "form_login_new:senha")))
        self.wait.until(ec.visibility_of_element_located((By.ID, "form_login_new:btnLogin")))

    def run(self):
        logging.info("Starting dag Ligga Telecom")
        self.home()
        self.login()
        self.get_invoice()

        logging.info("Finished download Ligga Telecom")
        self.webscrapper.shutdown()

    def __init__(self):
        self.config = ConfigFromEnv()  # Initialize logging handler also
        self.secrets = SecretsFactory(Secrets.LOCAL)
        self.webscrapper = Webscrapper()
        self.driver = self.webscrapper.driver
        self.wait = WebDriverWait(self.driver, 2)


if __name__ == '__main__':
    c = LiggaTelecom()
    c.run()
    logging.info("Finished download invoices from Ligga")
