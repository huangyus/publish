import base64
import datetime
import hashlib
import json
import os
import re
import time

import six
from Crypto.Cipher import AES
from django.utils.encoding import smart_str

from api.consumers import emit_notification


def utc2local(utc_st):
    now = time.time()
    local_time = datetime.datetime.fromtimestamp(now)
    utc_time = datetime.datetime.utcfromtimestamp(now)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st


def get_encryption_key(field_name='password', pk=None):
    """
    Generate key for encrypted password based on field name,
    ``settings.SECRET_KEY``, and instance pk (if available).

    :param field_name:
    :param pk: (optional) the primary key of the ``awx.conf.model.Setting``;
               can be omitted in situations where you're encrypting a setting
               that is not database-persistent (like a read-only setting)
    """
    from publish import settings
    h = hashlib.sha1()
    h.update(settings.SECRET_KEY.encode('utf-8'))
    if pk is not None:
        h.update(str(pk))
    h.update(field_name.encode('utf-8'))
    return h.digest()[:16]


def encrypt_value(value, field_name='password', skip_utf8=None):
    """
    Return content of the given instance and field name encrypted.
    """
    if skip_utf8:
        utf8 = False
    else:
        utf8 = type(value) == six.text_type
    value = smart_str(value)
    key = get_encryption_key(field_name)
    cipher = AES.new(key, AES.MODE_ECB)
    while len(value) % cipher.block_size != 0:
        value += '\x00'

    encrypted = cipher.encrypt(value)
    b64data = base64.b64encode(encrypted)
    tokens = ['$encrypted', 'AES', b64data.decode('utf-8')]
    if utf8:
        tokens.insert(1, 'UTF8')
    return '$'.join(tokens)


def decrypt_value(encryption_key, value):
    raw_data = value[len('$encrypted$'):]
    utf8 = raw_data.startswith('UTF8$')
    if utf8:
        raw_data = raw_data[len('UTF8$'):]
    algo, b64data = raw_data.split('$', 1)
    if algo != 'AES':
        raise ValueError('unsupported algorithm: %s' % algo)
    encrypted = base64.b64decode(b64data)
    cipher = AES.new(encryption_key, AES.MODE_ECB)
    value = cipher.decrypt(encrypted)
    if utf8:
        value = value.decode('utf-8')
        value = value.rstrip('\x00')
    return value


def set_color(line):
    line = line.replace('[0;0m', '')
    line = line.replace('', '')
    line = line.replace(' ', '&nbsp;')
    if ('Summary' in line) or ('------------' in line) or ('Total' in line):
        line = line.replace('[0;36m', '')
        line = {'color': 'darkcyan', 'text': line}
    elif "[0;33m" in line:
        line = line.replace('[0;33m', '')
        line = {'color': 'orange', 'text': line}
    elif "[0;32m" in line:
        line = line.replace('[0;32m', '')
        line = {'color': 'green', 'text': line}
    elif ("[0;31m" in line) or ("[0;1;31m" in line):
        line = line.replace('[0;31m', '').replace('[0;1;31m', '')
        line = {'color': 'red', 'text': line}
    elif "[0;36m" in line:
        line = line.replace('[0;36m', '')
        line = {'color': 'darkcyan', 'text': line}
    elif "[1;35m" in line:
        line = line.replace('[1;35m', '')
        line = {'color': 'tomato', 'text': line}
    elif "[0;35m" in line:
        line = line.replace('[0;35m', '')
        line = {'color': 'purple', 'text': line}
    elif "[1;30m" in line:
        line = line.replace('[1;30m', '')
        line = {'color': 'black', 'text': line}
    elif "[0;34m" in line:
        line = line.replace('[0;34m', '')
        line = {'color': 'blue', 'text': line}
    elif "[0;1;33m" in line:
        line = line.replace('[0;1;33m', '')
        line = {'color': 'gold', 'text': line}
    else:
        line = {'color': 'red', 'text': line}
    return line


def read_log(outfile):
    data = []
    state = None
    lines = ''
    logfile = open(outfile, 'r')
    while True:
        # current_position = logfile.tell()
        line = logfile.readline()
        if state:
            if re.match('(?=^\S+)(\W+\S+)*(?<= s)', lines):
                # logfile.seek(current_position)
                color_line = lines.split('\n')
                detail = []
                for l in color_line:
                    detail.append(set_color(l))
                failed = False if re.findall('Failed:\W+\d+', lines)[0].split(' ')[-1] == '0' else True
                host = re.findall('^\S+\d+\S+', lines)[0].split(':')[0].replace('[0;32m', '').replace('[0;1;31m', '').replace('[0;31m', '').replace('[0;0m', '')
                print({'host': host, 'failed': failed, 'detail': detail})
                if failed:
                    text = '%s      Failed' % host
                    color = 'red'
                    data.append({'color': color, 'text': text, 'detail': detail, 'failed': failed, 'host': host})
                else:
                    text = '%s      Success' % host
                    color = 'green'
                    data.append({'color': color, 'text': text, 'detail': detail, 'failed': failed, 'host': host})
                lines = ''
                state = None
        if re.search('Total run time', str(line)):
            state = True
        if re.findall('No response', lines) or re.findall('No minions', lines):
            detail = []
            color_line = lines.split('\n')
            for l in color_line:
                detail.append(set_color(l))
            try:
                host = re.findall('^\S+\d+\S+', lines)[0].split(':')[0].replace('[0;32m', '').replace('[0;1;31m', '').replace('[0;31m', '').replace('[0;0m', '').replace('[0;36m', '')
            except Exception as e:
                host = ''
            text = '%s      Failed' % host
            color = 'red'
            data.append({'color': color, 'text': text, 'detail': detail, 'failed': True, 'host': host})
            lines = ''
        if str(line) == 'end\n':
            logfile.close()
            print("文件读取结束")
            if len(lines) > 0:
                detail = []
                color_line = lines.split('\n')
                for l in color_line:
                    detail.append(set_color(l))
                try:
                    host = re.findall('^\S+\d+\S+', lines)[0].split(':')[0].replace('[0;32m', '').replace('[0;1;31m', '').replace('[0;31m', '').replace('[0;0m', '').replace('[0;36m', '')
                except Exception as e:
                    host = ''
                text = '%s      Failed' % host
                color = 'red'
                data.append({'color': color, 'text': text, 'detail': detail, 'failed': True, 'host': host})
            break
        lines += str(line)
    return data


def send_log(outfile, task_id, deploy_type):
    while True:
        if os.path.exists(outfile):
            break
        else:
            time.sleep(3)
    logfile = open(outfile, 'r')
    print("%s 日志文件打开成功" % outfile)
    tasklog = None
    if deploy_type == 'bs':
        from main.models import Business, TaskLog
        task = Business.objects.get(id=task_id)
        tasklog = TaskLog.objects.get(id=task.log_id)
    if deploy_type == 'bc':
        from main.models import Basic, TaskLog
        task = Basic.objects.get(id=task_id)
        tasklog = TaskLog.objects.get(id=task.log_id)
    logtext = []
    lines = ''
    state = None
    status = []
    recode = None
    while True:
        # current_position = logfile.tell()
        line = logfile.readline()
        if state:
            if re.match('(?=^\S+)(\W+\S+)*(?<= s)', lines):
                # logfile.seek(current_position)
                color_line = lines.split('\n')
                detail = []
                for l in color_line:
                    detail.append(set_color(l))
                if re.findall('Failed:\W+\d+', lines)[0].split(' ')[-1] == '0':
                    failed = False
                    recode = True
                else:
                    recode = False
                    failed = True
                host = re.findall('^\S+\d+\S+', lines)[0].split(':')[0].replace('[0;32m', '').replace('[0;1;31m', '').replace('[0;31m', '').replace('[0;0m', '')
                print({'host': host, 'failed': failed, 'detail': detail})
                if failed:
                    text = '%s      Failed' % host
                    color = 'red'
                    message = {'color': color, 'text': text, 'detail': detail, 'failed': failed, 'host': host}
                    emit_notification(task_id, {'message': message})
                    logtext.append(message)
                else:
                    text = '%s      Success' % host
                    color = 'green'
                    message = {'color': color, 'text': text, 'detail': detail, 'failed': failed, 'host': host}
                    emit_notification(task_id, {'message': message})
                    logtext.append(message)
                status.append(str(failed))
                state = ''
                lines = ''
        if re.search('Total run time', str(line)):
            state = True
        if re.findall('No response', lines) or re.findall('No minions', lines):
            recode = False
            detail = []
            color_line = lines.split('\n')
            for l in color_line:
                detail.append(set_color(l))
            try:
                host = re.findall('^\S+\d+\S+', lines)[0].split(':')[0].replace('[0;32m', '').replace('[0;1;31m', '').replace('[0;31m', '').replace('[0;0m', '').replace('[0;36m', '')
            except Exception as e:
                host = ''
            text = '%s      Failed' % host
            color = 'red'
            message = {'color': color, 'text': text, 'detail': detail, 'failed': True, 'host': host}
            emit_notification(task_id, {'message': message})
            lines = ''
        if str(line) == 'end\n':
            logfile.close()
            print("文件读取结束")
            if len(lines) > 0:
                detail = []
                color_line = lines.split('\n')
                for l in color_line:
                    detail.append(set_color(l))
                try:
                    host = re.findall('^\S+\d+\S+', lines)[0].split(':')[0].replace('[0;32m', '').replace('[0;1;31m', '').replace('[0;31m', '').replace('[0;0m', '').replace('[0;36m', '')
                except Exception as e:
                    pass
                text = '%s      Failed' % host
                color = 'red'
                message = {'color': color, 'text': text, 'detail': detail, 'failed': True, 'host': host}
                emit_notification(task_id, {'message': message})
                lines = ''
            emit_notification(task_id, {'message': 'end'})
            break
        lines += str(line)
    logtext = json.dumps(json.loads(tasklog.log_text) + logtext)
    tasklog.log_text = logtext
    tasklog.save()
    return recode


def workflow_sendlog(outfile, task_id):
    while True:
        if os.path.exists(outfile):
            break
        else:
            time.sleep(3)
    logfile = open(outfile, 'r')
    print("%s 日志文件打开成功" % outfile)
    lines = ''
    state = None
    status = []
    recode = None
    while True:
        current_position = logfile.tell()
        line = logfile.readline()
        if state:
            if re.match('(?=^\S+)(\W+\S+)*(?<= s)', lines):
                logfile.seek(current_position)
                color_line = lines.split('\n')
                detail = []
                for l in color_line:
                    detail.append(set_color(l))
                if re.findall('Failed:\W+\d+', lines)[0].split(' ')[-1] == '0':
                    failed = False
                    recode = True
                else:
                    failed = True
                    recode = False
                host = re.findall('^\S+\d+\S+', lines)[0].split(':')[0].replace('[0;32m', '').replace('[0;1;31m', '').replace('[0;31m', '').replace('[0;0m', '')
                print({'host': host, 'failed': failed, 'detail': detail})
                if failed:
                    text = '%s      Failed' % host
                    color = 'red'
                    message = {'color': color, 'text': text, 'detail': detail, 'failed': failed, 'host': host}
                    emit_notification(task_id, {'message': message})
                else:
                    text = '%s      Success' % host
                    color = 'green'
                    message = {'color': color, 'text': text, 'detail': detail, 'failed': failed, 'host': host}
                    emit_notification(task_id, {'message': message})
                status.append(str(failed))
                state = ''
                lines = ''
        if re.search('Total run time', str(line)):
            state = True
        if re.findall('No response', lines) or re.findall('No minions', lines):
            recode = True
            detail = []
            color_line = lines.split('\n')
            for l in color_line:
                detail.append(set_color(l))
            host = re.findall('^\S+\d+\S+', lines)[0].split(':')[0].replace('[0;32m', '').replace('[0;1;31m', '').replace('[0;31m', '').replace('[0;0m', '').replace('[0;36m', '')
            text = '%s      Failed' % host
            color = 'red'
            message = {'color': color, 'text': text, 'detail': detail, 'failed': True, 'host': host}
            emit_notification(task_id, {'message': message})
            lines = ''
        if str(line) == 'end\n':
            logfile.close()
            print("文件读取结束")
            emit_notification(task_id, {'message': 'end'})
            break
        lines += str(line)
    return recode
