import os
import tempfile
import time

from audio import (load_audio_captcha, click_download_audio,
                   check_download_finished)
from browser import set_chrome, load_SIPAC
from database import Database
from image import save_captcha_image

DATA_FOLDER = os.path.join(os.getcwd(), 'data')


class SIPAC():
    def __init__(self, download_dir=None):
        self.download_dir = download_dir
        if self.download_dir:
            os.chdir(self.download_dir)
        self.driver = None

    def start(self):
        self.driver = set_chrome(self.download_dir)

    def save_data(self, filename, delay=2.5):
        self.save_image(filename)
        time.sleep(delay)
        audio_loaded = self.save_audio(filename)
        if audio_loaded is False:
            print('Não foi possível carregar o áudio, tentando novo captcha.')
            self.save_data(filename)

    def save_image(self, filename):
        load_SIPAC(self.driver)
        filename = filename + '.png'
        save_captcha_image(self.driver, filename)

    def save_audio(self, filename):
        filename = filename + '.wav'
        download_finished = False
        while download_finished is False:
            player = load_audio_captcha(self.driver, retry=False)
            if not player:
                return False
            else:
                click_download_audio(self.driver, player)
                download_finished = check_download_finished()
        DOWNLOAD_NAME = 'GerarSomCaptcha.wav'
        os.rename(DOWNLOAD_NAME, filename)


if __name__ == '__main__':
    DATA_DIR = os.path.join(os.getcwd(), 'data')
    with tempfile.TemporaryDirectory() as tmp_dir:
        print(f'Working on: {tmp_dir}')
        time.sleep(5)
        db = Database()

        sipac = SIPAC(tmp_dir)
        sipac.start()

        for i in range(0, 500):
            print(i)
            filename = f'captcha_{str(i).zfill(3)}'
            sipac.save_data(filename=filename)

            image_file = f'{filename}.png'
            audio_file = f'{filename}.wav'

            image_data = open(image_file, 'rb').read()
            audio_data = open(audio_file, 'rb').read()

            db.insert_captcha(image_data, audio_data)

            os.remove(image_file)
            os.remove(audio_file)

    db.close()
    sipac.driver.close()
