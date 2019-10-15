import smtplib
import os
import json
import logger
import urllib
import urllib.request
import urllib.error


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
    proxies_file = 'proxies.txt'
    proxies = []
    proxy_index = 0
    mails = []
    mails_index = 0
    targets = []
    targets_index = 0
    required_files = ['mails.txt', 'targets.txt', 'proxies.txt']
    smtp_objects = {    # email hosts and hosts (if an error will be occurred while connecting one of them)
        'smtp.gmail.com': [465, 587]
    }
    mails_per_account = 5   # how much mails send per one mail
    proxy = True    # use proxy
    pause = False   # pause spamming
    version = '1.0.5'


def spam(text_from_file):
    print('[INFO] Starting spam (text: from file: {})'.format(text_from_file))
    if text_from_file in os.listdir('.'):
        with open(text_from_file, 'r') as text:
            text = text.read()
    else:
        print('[ERROR] File with text not found: {}'.format(text_from_file))
    for smtp_method in data.smtp_objects:
        print('[INFO] Connecting to the {}...'.format(smtp_method))
        try:
            for port in data.smtp_objects[smtp_method]:
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
                    else:
                        print('[INFO] Successfully connected: {}, port {}. Starting tls connection...'.format(smtp_method, port))
                        smtp.starttls()
                        print('[INFO] TLS connection started successfully')

                        update_vars = True
                        while data.mails_index < len(data.mails):
                            while not data.pause:
                                if update_vars:
                                    current_proxy_index = data.proxy_index
                                    current_target_index = data.targets_index
                                    current_mail_index = data.mails_index
                                    data.proxy_index += 1
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
                                    smtp.sendmail(current_mail_name, targets, text)
                                    print('[INFO] Login: {}, password {}: mail successfully sent'.format(current_mail_name,
                                                                                                         current_mail_password))
                                except Exception as exception_sending_mail:
                                    print('[ERROR] Login {}, password {}: can\'t send mail: {}'.format(current_mail_name,
                                                                                                       current_mail_password,
                                                                                                       str(exception_sending_mail)))
                                update_vars = True

                except Exception as exception_connecting:
                    print('[ERROR] {}: port {}: connection failed: {}'.format(smtp_method, port, str(exception_connecting)))
                    return

        except Exception as exception:
            print('[ERROR] An error occurred while spamming: {}'.format(str(exception)))


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


def test_proxies(test_url='google.com'):     # test url - without http or https (write it in proxies_type)
    logger.write('log', 'Testing https proxies...')
    bad_proxies = 0
    good_proxies = 0
    index = 1
    file = data.proxies_file
    try:
        print('This can take a while. Press ctrl+c to finish testing')
        if file in os.listdir('.'):
            with open(file, 'r') as proxies:
                proxies = proxies.read().split('\n')
        for proxy in proxies:
            valid = True
            try:
                proxy_handler = urllib.request.ProxyHandler({'https': proxy})
                opener = urllib.request.build_opener(proxy_handler)
                opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR'
                                                    ' 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; '
                                                    '.NET4.0E; InfoPath.3; Creative AutoUpdate v1.40.02)')]
                urllib.request.install_opener(opener)
                req = urllib.request.Request(f'https://{test_url}')
                sock = urllib.request.urlopen(req)
            except urllib.error.HTTPError as e:
                print('{}. {}: error: {}'.format(index, proxy, e))
                logger.write('log', '{}. {}: error: {}'.format(index, proxy, e))
                valid = False
            except Exception as detail:
                print('{}. {}: error: {}'.format(index, proxy, detail))
                valid = False
            if not valid:
                bad_proxies += 1
                _add_bad_proxy(proxy)
            else:
                good_proxies += 1
                print('{}. {}: valid'.format(index, proxy))
            index += 1
    except KeyboardInterrupt:
        print('Finishing test. Good proxies: {}, bad proxies: {}, totally proxies checked: {}'.format(good_proxies, bad_proxies, index - 1))
        logger.write('log', 'https proxies test were forcibly completed. Totally checked: {}; good proxies: {}; bad proxies: {}'.format(index - 1, good_proxies, bad_proxies))

    print('https proxies testing has successfully finished. Totally proxies checked: {}, bad proxies: {}, good proxies: {}'.format(index - 1, bad_proxies, good_proxies))
    logger.write('log', 'https proxies testing has successfully finished. Totally proxies checked: {}; bad proxies: {}; good proxies: {}'.format(index - 1, bad_proxies, good_proxies))


def _add_bad_proxy(proxy):
    with open('bad_proxy', 'a') as bad_proxies_file:
        logger.write('log', f'new bad proxy: {proxy}')
        bad_proxies_file.write(proxy + '\n')


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
    print('[INFO] Loading proxies from file:', data.proxies_file)
    with open(data.proxies_file, 'r') as proxies:
        data.proxies = proxies.read().split('\n')
    with open(data.mails_file, 'r') as mails:
        data.mails = mails.read().split('\n')
    with open(data.targets_file, 'r') as targets:
        data.targets = targets.read().split('\n')
    proxies_totally = 1
    mails_totally = 1
    targets_totally = 1
    for each in enumerate(data.proxies):
        index, value = each
        if value.strip() == '':
            del data.proxies[index]
        proxies_totally = index + 1
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
    for element in [['Proxies', proxies_totally], ['Mails', mails_totally], ['Targets', targets_totally]]:
        print('[INFO] {} loaded successfully ({} totally)'.format(element[0], element[1]))
    return True
