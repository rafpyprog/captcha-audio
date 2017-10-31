import os
import time

import fire
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from browser import set_chrome, load_SIPAC
from database import Database

CAPTCHA_WAV = 'GerarSomCaptcha.wav'


def check_too_many_requests_error(driver):
    TOO_MANY_REQUESTS = ('The remote server returned an error: (429) '
                         'Too Many Requests.')
    return TOO_MANY_REQUESTS in driver.page_source


def load_audio_captcha(driver, webdriverwait=2, wait_too_many_requests=5, retry=True):
    WAIT = WebDriverWait(driver, webdriverwait)
    SOUND = ('https://www.receita.fazenda.gov.br/Aplicacoes/SSL/ATFLA/'
             'Sipac.App/GerarSomCaptcha.aspx?sid=0.2556393534615946')
    driver.get(SOUND)

    try:
        player = WAIT.until(
                     EC.visibility_of_element_located((By.TAG_NAME, 'video')))
        time.sleep(0.25)
    except TimeoutException:
        if not retry:
            return False

        if check_too_many_requests_error(driver) is True:
            print('Too many requests.')
            time.sleep(wait_too_many_requests)
            # retry
            load_SIPAC(driver)
            player = load_audio_captcha(driver)
        else:
            raise ConnectionError('Erro inesperado.')

    return player


def click_download_audio(driver, player):
    action = webdriver.common.action_chains.ActionChains(driver)
    x, y = 270, -1
    action.move_to_element_with_offset(player, x, -1)
    action.click()
    action.perform()


def check_download_finished(timeout=2):
    print('Waiting Download')
    is_finished = False
    elapsed_time = 0
    start_time = time.time()

    while is_finished is False and elapsed_time <= timeout:
        files = [i for i in os.listdir() if i == 'GerarSomCaptcha.wav']
        is_finished = bool(files)
        elapsed_time = time.time() - start_time

    if is_finished:
        print('Download realizado com sucesso.')
    else:
        print('Erro no Download.')

    return is_finished


def get_captcha(driver, delay=2.85):
    load_SIPAC(driver)
    time.sleep(delay)
    player = load_audio_captcha(driver)
    click_download_audio(driver, player)


def save_captcha_audio(driver, filename):
    download_finished = False
    while download_finished is False:
        get_captcha(driver)
        download_finished = check_download_finished()
    DOWNLOAD_NAME = 'GerarSomCaptcha.wav'
    os.rename(DOWNLOAD_NAME, filename)


def main(n=10, download_dir=None, overwrite=False):
    if download_dir:
        if not os.path.isabs(download_dir):
            download_dir = os.path.join(os.getcwd(), download_dir)
    else:
        download_dir = os.getcwd()

    os.chdir(download_dir)
    print(download_dir)

    global driver
    try:
        driver = set_chrome(download_dir=download_dir)
        for i in range(0, n + 1):
            print(f'\n{i}')
            filename = f'captcha_{str(i).zfill(4)}.wav'
            file_exists = os.path.isfile(filename)

            if file_exists is False:
                save_captcha_audio(driver, filename)
            elif file_exists is True and overwrite is True:
                os.remove(path)
                save_captcha_audio(driver, filename)
            else:
                print(f'Overwrite is true. Skipping file {filename}.')
    finally:
        driver.quit()



if __name__ == '__main__':
    fire.Fire(main)
