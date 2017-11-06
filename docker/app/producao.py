import os
import time

from PIL import Image
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common import action_chains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from audio import click_download_audio, check_download_finished
from getdata import SIPAC
from image import save_captcha_image
from splitaudio import solve_captcha
from sox import silence


def open_tab(driver, url):
    driver.execute_script(f"window.open('{url}');")
    current_tab = sipac.driver.window_handles[-1]
    driver.switch_to_window(current_tab)
    return current_tab


def save_audio(driver, filename, download_name='GerarSomCaptcha.wav'):
    WAIT = WebDriverWait(driver, 5)
    audio_url = ('https://www.receita.fazenda.gov.br/Aplicacoes/SSL/ATFLA/'
                 'Sipac.App/GerarSomCaptcha.aspx?sid=0.2556393534615946')
    download_finished = False
    new_tab = open_tab(driver, audio_url)
    player = WAIT.until(
                 EC.visibility_of_element_located((By.TAG_NAME, 'video')))
    if not player:
        return False

    click_download_audio(driver, player)
    download_finished = check_download_finished(filename=download_name)
    if download_finished:
        os.rename(download_name, filename)
        return True
    else:
        return False


def get_audio(sipac, output, delay=3):
    sipac.load_SIPAC()
    driver = sipac.driver
    time.sleep(delay)
    save_audio(driver, output)
    if solve_captcha(output, clean=False):
        os.remove(output)
        handles = driver.window_handles
        driver.close()
        driver.switch_to_window(handles[0])
        save_captcha_image(driver, 'captcha.png')
        return True
    else:
        os.remove(output)
        handles = driver.window_handles
        driver.close()
        driver.switch_to_window(handles[0])
        get_audio(sipac, output)



OUTPUT = 'captcha-audio.wav'
sipac = SIPAC()
sipac.start()
get_audio(sipac, OUTPUT)
sipac.driver.quit()
Image.open('captcha.png')




os.system('rm *.wav && rm *.png')
