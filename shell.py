import spammer
import os
import re

spammer.init()


class update:
    @staticmethod
    def __element_in_file(file, element):
        if file in os.listdir('.'):
            with open(file, 'r') as file:
                file = file.read().split('\n')
            return True if element in file else False

    @staticmethod
    def proxies_file(file):
        if file in os.listdir('.'):
            spammer.data.proxies_file = file
        else:
            print('[ERROR] File with proxies not found!')

    @staticmethod
    def mails_file(file):
        if file in os.listdir('.'):
            spammer.data.mails_file = file
        else:
            print('[ERROR] File with mails not found!')

    @staticmethod
    def targets_file(file):
        if file in os.listdir('.'):
            spammer.data.targets_file = file
        else:
            print('[ERROR] File with targets not found!')

    @staticmethod
    def proxies(from_file):
        if from_file in os.listdir('.'):
            with open(spammer.data.proxies_file, 'a+') as current_proxies_file:
                with open(from_file, 'r') as new_proxies:
                    current_proxies = current_proxies_file.read().split('\n')
                    new_proxies = new_proxies.read().split('\n')
                    new_proxies_to_add = []
                    for proxy in current_proxies:
                        if proxy not in new_proxies and proxy.strip() != '':
                            new_proxies_to_add.append(proxy)

                    current_proxies_file.write('\n'.join(new_proxies_to_add) + '\n')
            print('[INFO] Proxies updated successfully')
        else:
            print('[ERROR] File with proxies not found!')

    @staticmethod
    def proxy(new_proxy):
        with open(spammer.data.proxies_file, 'a') as current_proxies:
            if not update.__element_in_file(new_proxy, spammer.data.proxies_file):
                current_proxies.write(new_proxy + '\n')
            else:
                print('[ERROR] Proxy exists!')
        print('[INFO] Proxy added successfully')

    @staticmethod
    def mail(new_mail):
        with open(spammer.data.mails_file, 'a') as mails_file:
            if not update.__element_in_file(new_mail, spammer.data.proxies_file):
                mails_file.write(new_mail + '\n')
        print('[INFO] Mail added successfully')

    @staticmethod
    def mails(from_file):
        if from_file in os.listdir('.'):
            with open(spammer.data.mails_file, 'a+') as current_mails_file:
                with open(from_file, 'r') as new_mails:
                    current_mails = current_mails_file.read().split('\n')
                    new_mails = new_mails.read().split('\n')
                    new_mails_to_add = []
                    for mail in current_mails:
                        if mail not in new_mails and mail.strip() != '':
                            new_mails_to_add.append(mail)

                    current_mails_file.write('\n'.join(new_mails_to_add) + '\n')
            print('[INFO] Mails updated successfully ({} totally)'.format(len(new_mails_to_add)))
        else:
            print('[ERROR] File with mails not found!')

    @staticmethod
    def target(new_target):
        with open(spammer.data.targets_file, 'a') as targets_file:
            if not update.__element_in_file(new_target, spammer.data.proxies_file):
                targets_file.write(new_target + '\n')
        print('[INFO] Target added successfully')

    @staticmethod
    def targets(from_file):
        if from_file in os.listdir('.'):
            with open(spammer.data.proxies_file, 'a+') as current_targets_file:
                with open(from_file, 'r') as new_targets:
                    current_targets = current_targets_file.read().split('\n')
                    new_targets = new_targets.read().split('\n')
                    new_targets_to_add = []
                    for target in current_targets:
                        if target not in new_targets and target.strip() != '':
                            new_targets_to_add.append(target)

                    current_targets_file.write('\n'.join(new_targets_to_add) + '\n')
            print('[INFO] Targets updated successfully ({} totally)'.format(len(new_targets_to_add)))
        else:
            print('[ERROR] File with targets not found!')


def parse(text, config=None):
    if config is None:
        config = {'prefix': '-', 'sub_prefix': '--', 'split': ' '}
    argument_prefix = config['prefix']
    subargument_prefix = config['sub_prefix']
    argument_split = config['split']
    result = {'nonarguments': [], 'arguments': [], 'sub_arguments': [], 'objects': {}}
    text_split = text.split(argument_split)
    tmp_object = {'result': '', 'state': 1}
    start_index = 0
    in_quotes = False
    for element in text_split:
        if element.strip() == '':
            continue
        if re.match(subargument_prefix, element) is not None:
            if not in_quotes:
                result['sub_arguments'].append(''.join(element[len(subargument_prefix):]))
            else:
                tmp_object['result'] += ''.join(element) + ' '
        elif re.match(argument_prefix, element) is not None:
            if not in_quotes:
                result['arguments'].append(''.join(element[len(argument_prefix):]))
            else:
                tmp_object['result'] += ''.join(element) + ' '
        elif element[0] == '"' and element[-1] == '"':
            result['objects'][''.join(text_split[text_split.index(element) - 1])] = ''.join(element[1:-1])
        elif element[0] == '"':
            start_index = text_split.index(element) - 1
            in_quotes = True
            if tmp_object['state'] == 1:
                tmp_object['state'] = 0
                tmp_object['result'] += ''.join(element[1:]) + ' '
        elif element[-1] == '"':
            if tmp_object['state'] == 0:
                tmp_object['result'] += ''.join(element[:-1])
            tmp_object['state'] = 1
            result['objects'][text_split[start_index]] = tmp_object['result']
            tmp_object['result'] = ''
            in_quotes = False
        else:
            if not in_quotes:
                result['nonarguments'].append(element)
            else:
                tmp_object['result'] += ''.join(element) + ' '
    return result


def runcmd(cmd):
    cmd = parse(cmd)
    cmd_text = cmd['nonarguments']
    update_commands = {
        'proxy-file': update.proxies_file,
        'mail-file': update.mails_file,
        'targets-file': update.targets_file,
        'proxy': update.proxy,
        'mail': update.mail,
        'target': update.target,
        'proxies': update.proxies,
        'mails': update.mails,
        'targets': update.targets,
    }
    another_commands = {
        'proxies-test': spammer.test_proxies,
        'pause': spammer.pause_spam,
        'continue': spammer.continue_spam,
        'spam': spammer.spam,
        'help': spammer.gethelp
    }
    try:
        if cmd_text[0] == 'update':
            update_commands[cmd_text[1]](cmd_text[2])
        elif cmd_text[0] == 'start':
            another_commands[cmd_text[1]](cmd_text[2])
        else:
            another_commands[cmd_text[0]]()
    except IndexError:
        print('[ERROR] Maybe, you forgot some arguments? Enter command "help"')
    except TypeError:
        print('[ERROR] Maybe, you forgot some arguments? Enter command "help"')
    except KeyError as exception:
        print('[ERROR] Unknown command: {}'.format(str(exception)))


if __name__ == '__main__':
    update.proxies(spammer.data.proxies_file)
    update.mails(spammer.data.mails_file)
    update.targets(spammer.data.targets_file)
    try:
        while True:
            cmd = input('CMD> ')
            if cmd.strip().lower() in ['quit', 'exit']:
                print('[INFO] Stopping spammer...')
                break
            runcmd(cmd)
    except KeyboardInterrupt:
        print('\n[INFO] Stopping spammer...')
