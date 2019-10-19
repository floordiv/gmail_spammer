import spammer
import os
import re
import threading
import json

spammer.init()


class update:
    @staticmethod
    def __element_in_file(file, element):
        if file in os.listdir('.'):
            with open(file, 'r') as file:
                file = file.read().split('\n')
            return True if element in file else False

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
    def proxies_file(file):
        if file in os.listdir('.'):
            spammer.data.proxies_file = file
        else:
            print('[ERROR] File with proxies not found!')

    @staticmethod
    def mail(new_mail):
        with open(spammer.data.mails_file, 'a') as mails_file:
            if not update.__element_in_file(new_mail, spammer.data.mails_file):
                mails_file.write(new_mail + '\n')
        spammer.data.mails.append(new_mail)
        print('[INFO] Mail added successfully')

    @staticmethod
    def mails(from_file):
        if from_file in os.listdir('.'):
            with open(spammer.data.mails_file, 'r+') as current_mails_file:
                with open(from_file, 'r') as new_mails:
                    current_mails = current_mails_file.read().split('\n')
                    new_mails = new_mails.read().split('\n')
                    new_mails_to_add = []
                    for mail in current_mails:
                        if mail not in new_mails:
                            new_mails_to_add.append(mail)
                    # print('Okay, you caught me. I agree, it\'s my fault. So, what\'s next? You will punish me? Fuck you!\n(actually, this'
                    #       ' is the thing I have to write to the file:', "\n".join(new_mails_to_add), ')')
                    current_mails_file.write('\n'.join(new_mails_to_add))
                    spammer.data.mails.append(new_mails_to_add)
            print('[INFO] Mails updated successfully ({} totally)'.format(len(new_mails_to_add)))
        else:
            print('[ERROR] File with mails not found!')

    @staticmethod
    def target(new_target):
        with open(spammer.data.targets_file, 'a') as targets_file:
            if not update.__element_in_file(new_target, spammer.data.target_file):
                targets_file.write(new_target + '\n')
        spammer.data.targets.append(new_target)
        print('[INFO] Target added successfully')

    @staticmethod
    def targets(from_file):
        if from_file in os.listdir('.'):
            with open(spammer.data.targets_file, 'r+') as current_targets_file:
                with open(from_file, 'r') as new_targets:
                    current_targets = current_targets_file.read().split('\n')
                    new_targets = new_targets.read().split('\n')
                    new_targets_to_add = []
                    for target in current_targets:
                        if target not in new_targets and target.strip() != '':
                            new_targets_to_add.append(target)

                    current_targets_file.write('\n'.join(new_targets_to_add) + '\n')
                    spammer.data.targets.append(new_targets_to_add)
            print('[INFO] Targets updated successfully ({} totally)'.format(len(new_targets_to_add)))
        else:
            print('[ERROR] File with targets not found!')

    @staticmethod
    def proxy(new_proxy):
        with open(spammer.data.proxies_file, 'a') as proxies_file:
            if not update.__element_in_file(new_proxy, spammer.data.proxies_file):
                proxies_file.write(new_proxy + '\n')
        spammer.data.mails.append(new_proxy)
        print('[INFO] Proxy added successfully')

    @staticmethod
    def proxies(from_file):
        if from_file in os.listdir('.'):
            with open(spammer.data.proxies_file, 'r+') as current_proxies_file:
                with open(from_file, 'r') as new_proxies:
                    current_proxies = current_proxies_file.read().split('\n')
                    new_proxies = new_proxies.read().split('\n')
                    new_proxies_to_add = []
                    for proxy in current_proxies:
                        if proxy not in new_proxies and proxy.strip() != '':
                            new_proxies_to_add.append(proxy)

                    current_proxies_file.write('\n'.join(new_proxies_to_add) + '\n')
                    spammer.data.targets.append(new_proxies_to_add)
            print('[INFO] Targets updated successfully ({} totally)'.format(len(new_proxies_to_add)))
        else:
            print('[ERROR] File with targets not found!')

    @staticmethod
    def edit_setting(name, new_arg):
        with open('settings.json', 'r') as settings_file:
            settings = json.load(settings_file)
        settings[name] = new_arg
        with open('settings.json', 'w') as new_settings:
            json.dump(settings, new_settings)


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
        'mail-file': update.mails_file,
        'targets-file': update.targets_file,
        'proxy-file': update.proxies_file,
        'mail': update.mail,
        'target': update.target,
        'proxy': update.proxy,
        'mails': update.mails,
        'targets': update.targets,
        'proxies': update.proxies,
        'set': update.edit_setting
    }
    another_commands = {
        'pause': spammer.pause_spam,
        'continue': spammer.continue_spam,
        'spam': spammer.spam,
        'help': spammer.gethelp
    }
    try:
        if cmd_text[0] == 'update':
            update_commands[cmd_text[1]](cmd_text[2])
        elif cmd_text[0] == 'start':
            if cmd_text[1] == 'spam':
                print('[HELP] Press ctrl+c to pause and enter "continue" to resume spam')
            if 'threads' in cmd['sub_arguments']:
                threads_arg_index = cmd['sub_arguments'].index('threads')
                threads = int(cmd['sub_arguments'][threads_arg_index])
            else:
                threads = 10
            if 'timeout' in cmd['sub_arguments']:
                timeout_arg_index = cmd['sub_arguments'].index('timeout')
                spammer.data.timeout = int(cmd['sub_arguments'][timeout_arg_index])
            for i in range(threads):
                var = threading.Thread(target=another_commands[cmd_text[1]], args=[str(cmd_text[2])])

                spammer.data.threads.append(var)
                var.start()
            for each in spammer.data.threads:
                each.join()
        elif cmd_text[0] == 'set':
            update_commands[cmd_text[0]](cmd_text[1], cmd_text[2])
        else:
            another_commands[cmd_text[0]]()
    except IndexError:
        print('[ERROR] Maybe, you forgot some arguments? Enter command "help"')
    except TypeError:
        print('[ERROR] Maybe, you forgot some arguments or entered them wrong? Enter command "help"')
    except KeyError as exception:
        print('[ERROR] Unknown command: {}'.format(str(exception)))


# __name__ = 'eger'
if __name__ == '__main__':
    try:
        print('Type "help" for more info')
        while True:
            cmd = input('CMD> ')
            if cmd.strip().lower() in ['quit', 'exit']:
                print('[INFO] Stopping spammer...')
                break
            runcmd(cmd)
    except KeyboardInterrupt:
        print('\n[INFO] Stopping spammer...')

