import smtplib
import os
import json
from traceback import format_exc
from time import sleep


class data:
    header = '''
    ╔══╦═══╦══╦╗──╔╦╗──╔╦═══╦═══╗
    ║╔═╣╔═╗║╔╗║║──║║║──║║╔══╣╔═╗║
    ║╚═╣╚═╝║╚╝║╚╗╔╝║╚╗╔╝║╚══╣╚═╝║
    ╚═╗║╔══╣╔╗║╔╗╔╗║╔╗╔╗║╔══╣╔╗╔╝
    ╔═╝║║──║║║║║╚╝║║║╚╝║║╚══╣║║║
    ╚══╩╝──╚╝╚╩╝──╚╩╝──╚╩═══╩╝╚╝   '''
    mails_file = 'mails.txt'         # files with data (binds)
    targets_file = 'targets.txt'
    mails = []
    mails_index = 0
    targets = []
    targets_index = 0
    threads = []
    err_text = False
    required_files = ['mails.txt', 'targets.txt']
    smtp_objects = {    # email hosts and hosts (if an error will be occurred while connecting one of them)
        'smtp.gmail.com': [465, 587]
    }
    mails_per_account = 5   # how much mails send per one mail
    proxy = True    # use proxy
    pause = False   # pause spamming
    version = '1.0.5'
    timeout = 0.1
    output = []


def print_err(err):
    if data.err_text:
        print('[DETAILS] Additional info about error:\n', err)


def init():
    print(data.header + 'by @floordiv,', 'version:', data.version, '\n')
    print('[INFO] Starting spammer...')

    errors = {'files_doesnt_exists': [], 'smtp_addresses_errors': [],}
    print('[INFO] Checking files...')
    for file in data.required_files:
        if file not in os.listdir('.'):
            errors['files_doesnt_exists'].append(file)
    if len(errors['files_doesnt_exists']) > 0:
        print('[FATAL] Files doesn\'t exists: {}'.format(', '.join(errors['files_doesnt_exists'])))
        return errors
    print('[INFO] All the required files exists')
    print('[INFO] Loading settings...')
    try:
        with open('settings.json', 'r') as settings:
            settings = json.load(settings)[0]
        print('[INFO] Settings loaded successfully. Applying...')

        for key in settings:
            # data.__dict__[key] = settings[key]
            setattr(data, key, settings[key])
        print('[INFO] Settings applied')
    except FileNotFoundError:
        print('[ERROR] Settings file not found. Using default values')
    with open(data.mails_file, 'r') as mails:
        data.mails = mails.read().split('\n')
    with open(data.targets_file, 'r') as targets:
        data.targets = targets.read().split('\n')
    mails_totally = 1
    targets_totally = 1
    for each in enumerate(data.mails):
        index2, value = each
        if value.strip() == '':
            del data.mails[index2]
        mails_totally = index2 + 1
    for each in enumerate(data.targets):
        index3, value = each
        if value.strip() == '':
            del data.targets[index3]
        targets_totally = index3 + 1
    if type(targets_totally / mails_totally) == int:
        data.mails_per_account = targets_totally / mails_totally
    for element in [['Mails', mails_totally], ['Targets', targets_totally]]:
        print('[INFO] {} loaded successfully ({} totally)'.format(element[0], element[1]))
    return True


def __get_valid_text(email, text):
    text = 'From: {}\n'.format(email) + text
    return text


def spam(text_from_file):
    print('[HELP] Press ctrl+c to pause and enter "continue" to resume spam')
    print('[INFO] Starting spam (text: from file: {})'.format(text_from_file))
    if text_from_file in os.listdir('.'):
        with open(text_from_file, 'r') as text:
            text = text.read()
    else:
        print('[ERROR] File with text not found: {}'.format(text_from_file))
    for smtp_method in data.smtp_objects:
        print('[INFO] Connecting to the {}...'.format(smtp_method))
        try:
            port_done = False
            for port in data.smtp_objects[smtp_method]:
                if port_done:
                    break
                try:
                    print('[INFO] {}: trying port {}'.format(smtp_method, port))
                    try:
                        smtp = smtplib.SMTP(smtp_method, port)
                    except:
                        try:
                            smtp = smtplib.SMTP_SSL(smtp_method, port)
                        except:
                            print('[ERROR] Failed to connect to the {}:{}'.format(smtp_method, port))
                            continue
                    print('[INFO] Successfully connected: {}, port {}. Starting tls connection...'.format(smtp_method, port))
                    smtp.starttls()
                    print('[INFO] TLS connection started successfully')

                    update_vars = True
                    while data.mails_index < len(data.mails):
                        while not data.pause:
                            try:
                                if update_vars:
                                    current_target_index = data.targets_index
                                    current_mail_index = data.mails_index
                                    data.targets_index += data.mails_per_account
                                    data.mails_index += 1
                                    update_vars = False
                                try:
                                    print('[INFO] Log in: {}'.format(data.mails[current_mail_index]))
                                except IndexError:
                                    update_vars = True
                                    break
                                current_mail_name, current_mail_password = data.mails[current_mail_index].split('/')
                                try:
                                    smtp.login(current_mail_name, current_mail_password)
                                    print('[INFO] Login {}, password {}: Logged in successfully'.format(current_mail_name,
                                                                                                        current_mail_password))
                                except Exception as exception_login:
                                    print('[ERROR] Login {}, password {}: can\'t login: {}'.format(current_mail_name, current_mail_password,
                                                                                                   str(
                                                                                                       exception_login)))
                                finished = False
                                targets = []
                                current_mails_per_account = data.mails_per_account
                                while not finished:
                                    if current_mails_per_account == 0:
                                        print('[INFO] Spam finished: no more targets')
                                        finished = True
                                        return True
                                    try:
                                        targets = [i for i in
                                                   data.targets[current_target_index:current_mail_index + current_mails_per_account]]
                                        finished = True
                                    except IndexError:
                                        current_mails_per_account -= 1
                                try:
                                    if targets is []:
                                        continue
                                    text = __get_valid_text(current_mail_name, text)
                                    sleep(data.timeout)
                                    smtp.sendmail(current_mail_name, targets, text)
                                    print('[INFO] Login: {}, password {}: mail successfully sent'.format(current_mail_name,
                                                                                                         current_mail_password))
                                except Exception as exception_sending_mail:
                                    print('[ERROR] Login {}, password {}: can\'t send mail: {}'.format(current_mail_name,
                                                                                                       current_mail_password,
                                                                                                       str(exception_sending_mail)))
                                    # print('[DETAILS] Additional info about error:\n', format_exc())
                                    print_err(format_exc())
                                update_vars = True
                            except KeyboardInterrupt:
                                data.pause = True
                                import shell
                                while True:
                                    user_input = input('CMD> ')
                                    if user_input == 'stop':
                                        print('[INFO] Stopping spammer...')
                                        for each in data.threads:
                                            each._stop()
                                        return
                                    shell.runcmd(user_input)

                except Exception as exception_connecting:
                    print('[ERROR] {}: port {}: connection failed: {}'.format(smtp_method, port, str(exception_connecting)))
                    # print('[DETAILS] More error information:\n', format_exc())
                    print_err(format_exc())
                    return

        except Exception as exception:
            print('[ERROR] An error occurred while spamming: {}'.format(str(exception)))
    data.proxy_index = 0
    data.mails_index = 0
    data.targets_index = 0


def pause_spam():
    data.pause = True


def continue_spam():
    data.pause = False


def gethelp():
    try:
        with open('help.txt', 'r') as help_text:
            print(help_text.read())
    except FileNotFoundError:
        print('[ERROR] Help is unavailable: manual file doesn\'t exists')
