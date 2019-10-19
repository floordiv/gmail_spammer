import smtplib
import os
import json
from traceback import format_exc
from time import sleep
import socket
import logger
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
    mails = []
    mails_index = 0
    targets = []
    targets_index = 0
    proxies = []
    proxy_index = 0
    threads = []
    bad_proxies = []
    developer = 0
    auto_proxy_test = False
    required_files = ['mails.txt', 'targets.txt']
    smtp_objects = {    # email hosts and hosts (if an error will be occurred while connecting one of them)
        'smtp.gmail.com': [465, 587]
    }
    mails_per_account = 5   # how much mails send per one mail
    proxy = True    # use proxy
    pause = False   # pause spamming
    version = '1.0.7'
    timeout = 0.1
    output = []


def recvline(sock):
    """Receives a line."""
    stop = 0
    line = ''
    while True:
        i = sock.recv(1)
        if i.decode('UTF-8') == '\n':
            stop = 1
        line += i.decode('UTF-8')
        if stop == 1:
            print('Stop reached.')
            break
    print('Received line: %s' % line)
    return line


class ProxySMTP(smtplib.SMTP):
    """Connects to a SMTP server through a HTTP proxy."""

    def __init__(self, host='', port=0, p_address='',p_port=0, local_hostname=None,
             timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Initialize a new instance.

        If specified, `host' is the name of the remote host to which to
        connect.  If specified, `port' specifies the port to which to connect.
        By default, smtplib.SMTP_PORT is used.  An SMTPConnectError is raised
        if the specified `host' doesn't respond correctly.  If specified,
        `local_hostname` is used as the FQDN of the local host.  By default,
        the local hostname is found using socket.getfqdn().

        """
        self.p_address = p_address
        self.p_port = p_port

        self.timeout = timeout
        self.esmtp_features = {}
        self.default_port = smtplib.SMTP_PORT

        if host:
            (code, msg) = self.connect(host, port)
            if code != 220:
                raise IOError(code, msg)

        if local_hostname is not None:
            self.local_hostname = local_hostname
        else:
            # RFC 2821 says we should use the fqdn in the EHLO/HELO verb, and
            # if that can't be calculated, that we should use a domain literal
            # instead (essentially an encoded IP address like [A.B.C.D]).
            fqdn = socket.getfqdn()

            if '.' in fqdn:
                self.local_hostname = fqdn
            else:
                # We can't find an fqdn hostname, so use a domain literal
                addr = '127.0.0.1'

                try:
                    addr = socket.gethostbyname(socket.gethostname())
                except socket.gaierror:
                    pass
                self.local_hostname = '[%s]' % addr

        smtplib.SMTP.__init__(self)

    def _get_socket(self, port, host, timeout):
        # This makes it simpler for SMTP to use the SMTP connect code
        # and just alter the socket connection bit.
        print('Will connect to:', (host, port))
        print('Connect to proxy.')
        new_socket = socket.create_connection((self.p_address,self.p_port), timeout)

        s = "CONNECT %s:%s HTTP/1.1\r\n\r\n" % (port,host)
        s = s.encode('UTF-8')
        new_socket.sendall(s)

        print('Sent CONNECT. Receiving lines.')
        for x in range(2):
            recvline(new_socket)

        print('Connected.')
        return new_socket


def test_proxies(test_url='google.com'):
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
    data.bad_proxies.append(proxy)


def print_err(err):
    if data.developer == 1:
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


def __get_correct_port(url, ports):
    result = ''
    for port in ports:
        try:
            smtplib.SMTP(url, port)
            return port
        except:
            pass
    return None


def spam(text_from_file):
    if text_from_file in os.listdir('.'):
        with open(text_from_file, 'r') as text:
            text = text.read()
    else:
        print('[ERROR] File with text not found: {}'.format(text_from_file))
    finished = False
    while not finished:
        while not data.pause:
            try:
                for url in data.smtp_objects:
                    current_mail_index = data.mails_index
                    current_target_index = data.targets_index
                    current_proxy_index = data.proxy_index
                    data.proxy_index += 1
                    data.mails_index += 1
                    data.targets_index += 1
                    if len(data.proxies) >= data.proxy_index:
                        data.proxy_index = 0
                    try:
                        good_port = __get_correct_port(url, data.smtp_objects[url])
                        if good_port is None:
                            print('[ERROR] Connection failed: bad ports')
                            print_err(format_exc())
                            finished = True
                            break
                        # conn_type = __get_conn_type(url, good_port)
                        conn = ProxySMTP(host=url, port=good_port, p_address=data.proxies[current_proxy_index].split(':')[0], p_port=data.proxies[current_proxy_index].split(':')[1])
                        if conn is None:
                            print('[ERROR] Connection failed: connection types are wrong! (usual and ssl)')
                            print_err(format_exc())
                            finished = True
                            break
                        try:
                            conn.starttls()
                        except Exception as exception_starting_tls:
                            print('[ERROR] TLS connection failed: {}'.format(exception_starting_tls))
                            print_err(format_exc())
                            continue
                        mail_login = data.mails[current_mail_index].split('/')[0]
                        mail_password = data.mails[current_mail_index].split('/')[1]
                        try:
                            conn.login(mail_login, mail_password)
                        except Exception as exception_login:
                            print('[ERROR] Login {}, password {}: login error: {}'.format(mail_login, mail_password, exception_login))
                            print_err(format_exc())
                            continue
                        __finished = False
                        targets = []
                        current_mails_per_account = data.mails_per_account
                        while not finished:
                            if current_mails_per_account == 0:
                                print('[INFO] Spam finished: no more targets')
                                finished = True
                                return True
                            try:
                                targets = [i for i in data.targets[current_target_index:current_mail_index + current_mails_per_account]]
                                finished = True
                            except IndexError:
                                current_mails_per_account -= 1
                        try:
                            if targets is []:
                                continue
                            text = __get_valid_text(mail_login, text)
                            sleep(data.timeout)
                            conn.sendmail(mail_login, targets, text)
                        except Exception as exception_sending_mail:
                            print('[ERROR] Mail send failure: login {}, password {}: {}'.format(mail_login, mail_password, exception_sending_mail))
                    except Exception as exception:
                        print('[ERROR] An exception occurred while spamming: {}'.format(exception))
                        print_err(format_exc())
                finished = True
                print('[INFO] Spam finished!')
            except KeyboardInterrupt:
                print('[INFO] Spam paused. Type "continue" to continue spam')
                import shell
                while True:
                    user_input = input('(paused) CMD> ')
                    shell.runcmd(user_input)

    # for smtp_method in data.smtp_objects:
    #     print('[INFO] Connecting to the {}...'.format(smtp_method))
    #     try:
    #         port_done = False
    #         for port in data.smtp_objects[smtp_method]:
    #             if port_done:
    #                 break
    #             try:
    #                 print('[INFO] {}: trying port {}'.format(smtp_method, port))
    #                 try:
    #                     smtp = smtplib.SMTP(smtp_method, port)
    #                 except:
    #                     try:
    #                         smtp = smtplib.SMTP_SSL(smtp_method, port)
    #                     except:
    #                         print('[ERROR] Failed to connect to the {}:{}'.format(smtp_method, port))
    #                         continue
    #                 print('[INFO] Successfully connected: {}, port {}. Starting tls connection...'.format(smtp_method, port))
    #                 smtp.starttls()
    #                 print('[INFO] TLS connection started successfully')
    #
    #                 update_vars = True
    #                 while data.mails_index < len(data.mails):
    #                     while not data.pause:
    #                         try:
    #                             if update_vars:
    #                                 current_target_index = data.targets_index
    #                                 current_mail_index = data.mails_index
    #                                 data.targets_index += data.mails_per_account
    #                                 data.mails_index += 1
    #                                 update_vars = False
    #                             try:
    #                                 print('[INFO] Log in: {}'.format(data.mails[current_mail_index]))
    #                             except IndexError:
    #                                 update_vars = True
    #                                 break
    #                             current_mail_name, current_mail_password = data.mails[current_mail_index].split('/')
    #                             try:
    #                                 smtp.login(current_mail_name, current_mail_password)
    #                                 print('[INFO] Login {}, password {}: Logged in successfully'.format(current_mail_name,
    #                                                                                                     current_mail_password))
    #                             except Exception as exception_login:
    #                                 print('[ERROR] Login {}, password {}: can\'t login: {}'.format(current_mail_name, current_mail_password,
    #                                                                                                str(
    #                                                                                                    exception_login)))
    #                             finished = False
    #                             targets = []
    #                             current_mails_per_account = data.mails_per_account
    #                             while not finished:
    #                                 if current_mails_per_account == 0:
    #                                     print('[INFO] Spam finished: no more targets')
    #                                     finished = True
    #                                     return True
    #                                 try:
    #                                     targets = [i for i in
    #                                                data.targets[current_target_index:current_mail_index + current_mails_per_account]]
    #                                     finished = True
    #                                 except IndexError:
    #                                     current_mails_per_account -= 1
    #                             try:
    #                                 if targets is []:
    #                                     continue
    #                                 text = __get_valid_text(current_mail_name, text)
    #                                 sleep(data.timeout)
    #                                 smtp.sendmail(current_mail_name, targets, text)
    #                                 print('[INFO] Login: {}, password {}: mail successfully sent'.format(current_mail_name,
    #                                                                                                      current_mail_password))
    #                             except Exception as exception_sending_mail:
    #                                 print('[ERROR] Login {}, password {}: can\'t send mail: {}'.format(current_mail_name,
    #                                                                                                    current_mail_password,
    #                                                                                                    str(exception_sending_mail)))
    #                                 # print('[DETAILS] Additional info about error:\n', format_exc())
    #                                 print_err(format_exc())
    #                             update_vars = True
    #                         except KeyboardInterrupt:
    #                             data.pause = True
    #                             import shell
    #                             while True:
    #                                 user_input = input('CMD> ')
    #                                 if user_input == 'stop':
    #                                     print('[INFO] Stopping spammer...')
    #                                     for each in data.threads:
    #                                         each._stop()
    #                                     return
    #                                 shell.runcmd(user_input)
    #
    #             except Exception as exception_connecting:
    #                 print('[ERROR] {}: port {}: connection failed: {}'.format(smtp_method, port, str(exception_connecting)))
    #                 # print('[DETAILS] More error information:\n', format_exc())
    #                 print_err(format_exc())
    #                 return

        # except Exception as exception:
        #     print('[ERROR] An error occurred while spamming: {}'.format(str(exception)))
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
