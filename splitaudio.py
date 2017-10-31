import io
import os
import re
from subprocess import Popen, PIPE
import tempfile

import numpy as np

from sox import silence
from database import Database


LETTER_AUDIO_FILE = 'letter.wav'


def file_info(filepath):
    get_info = ['sox', '--info', filepath]
    process = Popen(get_info, stdout=PIPE, encoding='utf-8')
    info, err = process.communicate()
    return info.splitlines()


def split_letters(audio_file, duration, threshold, output=LETTER_AUDIO_FILE,
                  verbosity=2):
    threshold = str(threshold) + '%'
    cmd = ['sox', f'-V{verbosity}', audio_file, output,
           f'silence 1 {duration} {threshold} 1 {duration} {threshold}',
           ': newfile', ': restart']
    os.system(cmd)


def count_letters(letter_audio_file):
    name, extension = letter_audio_file.split('.')
    count = len([i for i in os.listdir() if i.startswith(name)])
    return count


def assert_minimum_size(letters):
    MIN_SIZE = 2500
    MAX_SIZE = 11000
    SOUND_ERROR = 44
    valid_letters_count = 0

    for letter in letters:
        size = os.path.getsize(letter)
        if size == SOUND_ERROR:
            os.remove(letter)
            continue
        if MIN_SIZE < size < MAX_SIZE and valid_letters_count < 6:
            valid_letters_count += 1
        else:
            return False

    return valid_letters_count == 6


def validate_results():
    letters = os.listdir()
    return assert_minimum_size(letters)


def clean_up(letter_audio_file):
    name, extension = letter_audio_file.split('.')
    letters = [i for i in os.listdir() if i.startswith(name)]
    for i in letters:
        filepath = os.path.join(os.getcwd(), i)
        os.remove(filepath)


def get_captchas():
    pattern = '^captcha_\d{4}\.wav$'
    cwd = os.getcwd()
    captchas = [os.path.join(cwd, i) for i in os.listdir()
                if re.match(pattern, i)]
    return captchas


def best_performance_at_end(total, processed, sucess):
    remainign = total - processed
    return (remainign + sucess) / total


def can_beat_target(target, best_performance):
    if best_performance < target:
        return False
    else:
        return True


def process_capthcas(captchas, duration, threshold, target=0):
    conta_validos = 0
    performance = 0
    for n, captcha in enumerate(captchas):
        split_letters(captcha, duration, threshold)
        is_valid = validate_results(LETTER_AUDIO_FILE)
        if is_valid:
            conta_validos += 1

        performance = conta_validos / len(captchas)
        clean_up(LETTER_AUDIO_FILE)

    print('duration:', '{0:.4f}'.format(duration),
          'threshold:', '{0:.4f}'.format(threshold),
          '| Performance:', '{0:.4f}'.format(performance),
          'Target:', '{0:.4f}'.format(target))

    return performance


def log_performance(duration, threshold, performance, log='log.txt'):
    values = (duration, threshold, performance)
    data = ';'.join([str.format('{0:.4f}', i) for i in values])
    with open(log, 'a') as f:
        f.write(data + '\n')


def solve_captcha(captcha, clean=True, temp_dir=None):
    MIN_DURATION, MAX_DURATION, STEP_DURATION = 0, 0.175 + 0.025, 0.025
    MIN_THRESHOLD, MAX_THRESHOLD, STEP_THRESHOLD = 6.9, 13.10 + 0.10, 0.10

    for t in np.arange(MIN_THRESHOLD, MAX_THRESHOLD, STEP_THRESHOLD):
        for d in np.arange(MIN_DURATION, MAX_DURATION, STEP_DURATION):
            solved = False
            letter_count = silence(captcha, d, t, cwd=temp_dir)
            if letter_count >= 6:
                solved = validate_results()
            if solved:
                print('    Resultado:', d, t, 'SOLVED!')
                if clean:
                    clean_up(LETTER_AUDIO_FILE)
                return d, t
            clean_up(LETTER_AUDIO_FILE)
    print('    Resultado:', 'NOT SOLVED.')
    return False


def save_result(resultado, log='log.txt'):
    with open(log, 'a') as f:
        f.write('{0:.4f}'.format(resultado[0]) + ';' +
                '{0:.4f}'.format(resultado[1]) + ';' + '\n')


if __name__ == '__main__':
    HERE = os.getcwd()
    db = Database()
    captchas = [io.BytesIO(i[2]) for i in db.get_captchas()]

    stat_duration = [9999, 0]  # d, t
    stat_threshold = [9999, 0]
    resolvidos = 0
    performance = 0

    for n, c in enumerate(captchas):
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            print(f'\n{n} - {temp_dir}')
            resultado = solve_captcha(c, temp_dir=temp_dir)
            if resultado:
                stat_duration[0] = min(stat_duration[0], resultado[0])
                stat_duration[1] = max(stat_duration[1], resultado[0])

                stat_threshold[0] = min(stat_threshold[0], resultado[1])
                stat_threshold[1] = max(stat_threshold[1], resultado[1])

                resolvidos += 1
                save_result(resultado)
            performance = resolvidos / (n + 1)

            print('Duration    :', stat_duration)
            print('Threshold   :', stat_threshold)
            print('Performance :', '{0:.2f}%'.format(performance * 100))
