import os

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def set_chrome(download_dir=None, headless=False):
    if not download_dir:
        download_dir = os.getcwd()
    else:
        if os.path.isabs(download_dir) is False:
            download_dir = os.path.join(os.getcwd(), download_dir)
            print(download_dir)
    options = ChromeOptions()
    prefs = {"download.default_directory": download_dir}
    options.add_experimental_option("prefs", prefs)
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    return Chrome(chrome_options=options)


def load_SIPAC(driver, webdriverwait=5):
    WAIT = WebDriverWait(driver, webdriverwait)
    SIPAC = 'https://www.receita.fazenda.gov.br/Aplicacoes/SSL/ATFLA/Sipac.App/'
    driver.get(SIPAC)
    WAIT.until(EC.visibility_of_element_located((By.ID, 'imgcaptcha')))
