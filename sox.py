import io
import os
from subprocess import Popen, PIPE

import numpy as np

from database import Database


def parse_stdout(stdout):
    info = {}
    lines = [i for i in stdout.splitlines() if i != '']
    for i in lines:
        key, value = [i.strip() for i in i.split(':', 1)]
        info[key] = value
    return info


def info(audio_file, encoding='UTF-8'):
    if isinstance(audio_file, str):
        infile = audio_file
        input_data = None
        stdin = None
    else:
        infile = '−'
        input_data = audio_file.getvalue()
        stdin=PIPE

    cmd = f'sox --info {infile}'
    proc = Popen(cmd, stdout=PIPE, stdin=stdin)
    stdout, err = proc.communicate(input=input_data)
    info = stdout.decode(encoding=encoding)
    return parse_stdout(info)


def silence(infile, duration, threshold, output='letter.wav',
                  verbosity=2):

    threshold = str(threshold) + '%'
    input_data = None
    stdin = None

    if isinstance(infile, io._io.BytesIO):
        input_data = infile.getvalue()
        infile = '−'
        stdin = PIPE

    cmd = (f'sox -V{verbosity} -t wav {infile} "{output}" silence 1 {duration} '
           f'{threshold} 1 {duration} {threshold} : newfile : restart')

    proc = Popen(cmd, stdin=stdin)
    out, err = proc.communicate(input=input_data)
    return proc.returncode

db = Database()
captcha = db.get_captcha(1)
data = captcha.fetchall()[0][1]
audio = io.BytesIO(data)

info('letter001.wav')
import tempfile

for i in np.arange(6, 13, 0.25):
    for j in np.arange(0, 0.175, 0.025):
        with tempfile.TemporaryDirectory() as tmp:
            output = os.path.join(tmp, 'letter.wav')
            silence(audio, j, i, output=output, verbosity=2)
            count_files = len(os.listdir(tmp))
            if count_files >= 6:
                print(j, i, count_files)







info('letter.wav')
