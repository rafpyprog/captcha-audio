import io
import os
import re
import time

from IPython import display
from PIL import Image

from database import Database


def load_image(data):
    im = io.BytesIO(data)
    return Image.open(im)

DATA_FOLDER = os.path.join(os.getcwd(), 'data')
db = Database()

unsolved_captchas = db.get_captchas(solution=False)

##
for n, captcha in enumerate(unsolved_captchas):
    data = captcha[1]
    image = load_image(data)
    display.clear_output()
    display.display(image)
    i = input('Solução:')
    if n == 10:
        break

db.close()
