from multiprocessing import Pool, Value, Array, Process
import os
from multiprocessing.pool import ThreadPool
import pickle
import queue
import re
import shutil
import tempfile
import threading
import time

from PIL import Image
from pyvirtualdisplay import Display
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common import action_chains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from audio import click_download_audio, check_download_finished
from features import extract_audio_file_features
from getdata import SIPAC
from image import save_captcha_image
from splitaudio import solve_captcha
from sox import silence
import splitaudio



def open_tab(driver, url):
    driver.execute_script(f"window.open('{url}');")
    current_tab = driver.window_handles[-1]
    driver.switch_to_window(current_tab)
    return current_tab


def save_audio(driver, filename, download_name='GerarSomCaptcha.wav'):

    #WAIT = WebDriverWait(driver, 5)
    audio_url = ('https://www.receita.fazenda.gov.br/Aplicacoes/SSL/ATFLA/'
                 'Sipac.App/GerarSomCaptcha.aspx?sid=0.2556393534615946')

    session_id = driver.get_cookies()[0]
    cookie = f'{session_id["name"]}={session_id["value"]}'
    curl = f'curl -v --insecure --cookie "{cookie}" {audio_url} --output {filename}'
    print(curl)
    os.system(curl)

    #download_finished = False
    #new_tab = open_tab(driver, audio_url)
    #player = WAIT.until(
    #             EC.visibility_of_element_located((By.TAG_NAME, 'video')))
    #if not player:
    #    print('Player não abriu.')
    #    driver.get_screenshot_as_file('screen.png')
    #    return False

    #click_download_audio(driver, player)
    #download_finished = check_download_finished(filename=download_name)
    #if download_finished:
    #try:
    #    os.rename(download_name, filename)
    #except FileExistsError:
    #    os.remove(filename)
    #    os.rename(download_name, filename)
    return True
    #else:
    #    print('Erro no download')
    #    return False


def load_model(filename):
    with open(filename, 'rb') as f:
        model = pickle.loads(f.read())
    return model




def get_captcha(output='captcha-audio.wav', delay=3, save_image=False):
    sipac = SIPAC()
    sipac.start()
    sipac.load_SIPAC()
    driver = sipac.driver
    time.sleep(delay)
    save_audio(driver, output, download_name='GerarSomCaptcha.aspx')
    if save_image:
        #handles = driver.window_handles
        #driver.close()
        #driver.switch_to_window(handles[0])
        save_captcha_image(driver, 'captcha.png')
    return driver


def solver(audio_file, model, min_threshold=6.9, max_threshold=13.10):
    print(f'Iniciando solver')
    start_dir = os.getcwd()
    temp_dir = tempfile.TemporaryDirectory()
    shutil.copyfile(audio_file, os.path.join(temp_dir.name, audio_file))


    threshold={'min': min_threshold, 'max': max_threshold, 'step': 0.10}
    if solve_captcha(audio_file, threshold=threshold, clean=False,
                     temp_dir=temp_dir.name, use_finished_flag=True):
        pattern = '^letter\d{3}\.wav$'
        caracteres = sorted([os.path.join(temp_dir.name, fn) for fn in os.listdir(temp_dir.name) if re.match(pattern, fn)])
        captcha = ''
        for ch in caracteres:
            features = extract_audio_file_features(ch)
            prediction = model.predict(features)
            captcha = ''.join([captcha, prediction[0]])
        return captcha
    else:
        return False


def worker():
    while True:
        item = q.get()
        if item is None:
            break
        solucoes.put(solver(*item))
        q.task_done()

if __name__ == '__main__':
    print('Starting Virtual Display')
    display = Display(visible=False)
    display.start()

    CAPTCHA = 'captcha-audio.wav'
    driver = get_captcha(save_image=True)

    KNN = load_model('model.pkl')

    thresholds = []
    start = min_threshold = 6.9
    n_threads = 4
    size = (13.2 - 6.9) / n_threads

    for i in range(n_threads):
        max_threshold = start + size
        thresholds.append((CAPTCHA, KNN, start, max_threshold))
        start = max_threshold

    start_time = time.time()

    q = queue.Queue()
    solucoes = queue.Queue()

    threads = []
    for i in range(n_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for item in thresholds:
        q.put(item)


    solucao_captcha = ''
    count = 0
    while not solucao_captcha:
        solucao_captcha = solucoes.get(block=True)
        if solucao_captcha and solucao_captcha != '':
            print('CAPTCHA:', solucao_captcha)
            #print('Finalizando workers no while')
            for i in range(n_threads):
                q.put(None)
            #print('Finalizando threads no while')
            for t in threads:
                t.join()
            break
        if solucao_captcha is False:
            #print('Um falso no while')
            count += 1

        if count == n_threads:
            print('FIM')
            for i in range(n_threads):
                q.put(None)
            print('Finalizando threads')
            for t in threads:
                t.join()
            break



    end_time = round(time.time() - start_time, 2)
    print(end_time)


    driver.find_element_by_id('ctl00_CPL_TextBoxCPF').send_keys('02444948190')
    driver.find_element_by_id('ctl00_CPL_TextBoxSenha').send_keys('derep245')
    driver.find_element_by_id('captcha').send_keys(solucao_captcha)

    print('FIM')
    driver.quit()
    display.stop()
    os.remove(CAPTCHA)

    # stop workers
