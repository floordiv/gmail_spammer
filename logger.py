import datetime
import os


def write(text, file):
    if 'log' not in os.listdir('.'):
        os.mkdir('log')
    if file in os.listdir('log'):
        mode = 'a'
    else:
        mode = 'w'

    with open(f'log/{file}', mode) as log_file:
        log_file.write(f'[{str(datetime.datetime.today()).split(".")[0]}] {text}\n')
