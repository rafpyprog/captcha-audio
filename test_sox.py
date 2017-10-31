import io
from subprocess import Popen, PIPE

import numpy as np

from database import Database


def split_letters(audio_file, duration, threshold, output='letter.wav',
                  verbosity=2):
    threshold = str(threshold) + '%'

    if isinstance(audio_file, io._io.BytesIO):
        print('ok')
        infile = '−'
        input_data = audio_file.getvalue()
        stdin = PIPE
    else:
        infile = audio_file
        input_data = None
        stdin = None


    cmd = (f'sox -V{verbosity} {infile} {output} silence 1 {duration} '
           f'{threshold} 1 {duration} {threshold} : newfile : restart')
    proc = Popen(cmd, stdin=stdin, stdout=PIPE)

    out, err = proc.communicate(input=input_data)
    print(out.decode().splitlines(), err)
    return proc.returncode

db = Database()
captcha = db.get_captcha(1)
data = captcha.fetchall()[0][1]
audio = io.BytesIO(data)

split_letters(audio, 0.12, 5, verbosity=3)

for t in np.arange(1, 12, 0.5):
    for d in np.arange(0, 0.175, 0.05):
        split_letters(audio, d, t, verbosity=3)
