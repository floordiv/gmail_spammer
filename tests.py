from traceback import format_exc
import os


class data:
    pause = False
    mails = ['pavloromanenko25@gmail.com/password_for_pavloromanenko', 'rustakss@gmail.com/password_for_rustak']
    mails_index = 0
    targets_index = 0
    targets = ['alt.floordiv@gmail.com', 'target@gmail.com']
    mails_per_account = 1


def spam(text_from_file):
    print('[INFO] Starting spam (text: from file: {})'.format(text_from_file))
    smtp_objects = {
        'smtp.gmail.com': [467, 585]
    }
    if text_from_file in os.listdir('.'):
        with open(text_from_file, 'r') as text:
            text = text.read()
    else:
        print('[ERROR] File with text not found: {}'.format(text_from_file))
    for smtp_method in smtp_objects:
        print('[INFO] Connecting to the {}...'.format(smtp_method))
        try:
            port_done = False
            for port in smtp_objects[smtp_method]:
                if port_done:
                    break
                try:
                    print('[INFO] {}: trying port {}'.format(smtp_method, port))
                    try:
                        print('Connecting with usual connect type')
                        raise ConnectionRefusedError
                    except ConnectionRefusedError:
                        try:
                            print('Connecting with ssl')
                            # smtp = smtplib.SMTP_SSL(smtp_method, port)
                        except:
                            print('[ERROR] Failed to connect to the {}:{}'.format(smtp_method, port))
                            continue
                    port_done = True
                    print('[INFO] Successfully connected: {}, port {}. Starting tls connection...'.format(smtp_method, port))
                    # smtp.starttls()
                    print('[INFO] TLS connection started successfully')

                    update_vars = True
                    while data.mails_index < len(data.mails):
                        while not data.pause:
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
                                # smtp.login(current_mail_name, current_mail_password)
                                print('[INFO] Login {}, password {}: Logged in successfully'.format(current_mail_name,
                                                                                                    current_mail_password))
                            except Exception as exception_login:
                                print('[ERROR] Login {}, password {}: can\'t login: {}'.format(current_mail_name, current_mail_password,
                                                                                               str(
                                                                                                   exception_login)))
                                continue
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
                                # smtp.sendmail(current_mail_name, targets, text)
                                print('[INFO] Login: {}, password {}: mail successfully sent'.format(current_mail_name,
                                                                                                     current_mail_password))
                            except Exception as exception_sending_mail:
                                print('[ERROR] Login {}, password {}: can\'t send mail: {}'.format(current_mail_name,
                                                                                                   current_mail_password,
                                                                                                   str(exception_sending_mail)))
                                print('[DETAILS] Additional info about error:\n', format_exc())
                            update_vars = True

                except Exception as exception_connecting:
                    print('[ERROR] {}: port {}: connection failed: {}'.format(smtp_method, port, str(exception_connecting)))
                    print('[DETAILS] More error information:\n', format_exc())
                    return

        except Exception as exception:
            print('[ERROR] An error occurred while spamming: {}'.format(str(exception)))
    data.proxy_index = 0
    data.mails_index = 0
    data.targets_index = 0


print(spam('text.txt'))
