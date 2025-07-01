import paramiko
import subprocess
import datetime


def ssh_responce():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('192.168.0.231', 22, username='user', password='123456')
    stdin, stdout, stderr = ssh.exec_command('ps au')
    return stdout.readlines()


def process_parser(line):
    user, PID, CPU, MEM, VSZ, RSS, TTY, STAT, START, TIME, *COMMAND = line.split()
    return {
        'user': user,
        'cpu': float(CPU),
        'memory': float(MEM),
        'name': COMMAND[0]
    }


def add_user(process_paraneters):
    for user in user_list:
        if process_paraneters.get('user') == user['user_name']:
            user['process_count'] += 1
            return 0
    user_list.append({'user_name': process_parser(line).get('user'),
                      'process_count': 1})
    return 0


def max_update(key, process_parameters, current_max_value_proces):
    if current_max_value_proces['value'] < process_parameters[key]:
        current_max_value_proces = {'name': process_parameters['name'],
                                    'value': process_parameters[key]}
    return current_max_value_proces


def report_data():
    template = (f'Отчёт о состоянии системы:\n'
                f'Пользователи системы: ')
    for user in user_list:
        template += f'{user['user_name']}, '

    template += (f'\nПроцессов запущено: {proces_count}\n'
                 f'Пользовательских процессов: \n')

    for user in user_list:
        template += f'{user['user_name']}: {user['process_count']}\n'

    template += ('Всего памяти используется: {memory_count} mb\n'
                 f'Всего CPU используется: {cpu_resurce_count}%\n'
                 f"Больше всего памяти использует: ({max_memory_proces['name'][:20]}) {max_memory_proces['value']} mb\n"
                 f"Больше всего CPU использует: ({max_cpu_resurce_proces['name'][:20]}) {max_cpu_resurce_proces['value']} %\n")

    return template


lines = ssh_responce()
user_list = []
proces_count = 0
memory_count = 0
cpu_resurce_count = 0
max_memory_proces = {'name': 'ни один процесс не использует память',
                     'value': 0}
max_cpu_resurce_proces = {'name': 'ни один процесс не использует cpu',
                          'value': 0}

for line in lines[1:]:
    proces_count += 1
    memory_count += process_parser(line)['memory']
    cpu_resurce_count += process_parser(line)['cpu']
    add_user(process_parser(line))
    max_memory_proces = max_update('memory', process_parser(line), max_memory_proces)
    max_cpu_resurce_proces = max_update('cpu', process_parser(line), max_cpu_resurce_proces)
    print(process_parser(line))
print(report_data())

filename = datetime.datetime.now().strftime('%d-%m-%Y-%H:%M-scan.txt')
with open(filename, 'w') as f:
    f.write(report_data())
