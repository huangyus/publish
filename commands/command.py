import json
import os
import socket
import sys
from datetime import datetime

import paramiko
import subprocess

from django.conf import settings
from api.consumers import emit_notification
from utils.common import utc2local


def localComannd(cmd):
    (recode, data) = subprocess.getstatusoutput(cmd)
    return recode, data


def SSHCommand(cmd, logfile):
    ENV = ['export LANG=zh_CN.UTF-8', 'export LC_CTYPE=zh_CN.UTF-8']
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if settings.SALT_MASTER_PASS:
            ssh_client.connect(settings.SALT_MASTER, username=settings.SALT_MASTER_USER, password=settings.SALT_MASTER_PASS, port=settings.SALT_MASTER_PORT, timeout=6000)
        elif settings.SALT_MASTER_KEY:
            ssh_key = paramiko.RSAKey.from_private_key_file(settings.SALT_MASTER_KEY)
            ssh_client.connect(settings.SALT_MASTER, username=settings.SALT_MASTER_USER, pkey=ssh_key, port=settings.SALT_MASTER_PORT, timeout=6000)
        else:
            ssh_client.connect(settings.SALT_MASTER, username=settings.SALT_MASTER_USER, port=settings.SALT_MASTER_PORT, timeout=6000)
    except (socket.error, paramiko.AuthenticationException, paramiko.SSHException) as message:
        print("ERROR: SSH connection to " + settings.SALT_MASTER + " failed: " + str(message))
        sys.exit(1)
    command = " && ".join(ENV)
    command = command + " && " + cmd
    stdin, stdout, stderr = ssh_client.exec_command(command)
    data = ''.join(stdout.readlines())
    with open(logfile, 'a') as f:
        f.write(data)
    code = stdout.channel.recv_exit_status()
    return code, data


def SFTPCommand(local_file, remote_dir, filename):
    ssh_client = paramiko.Transport((settings.SALT_MASTER, settings.SALT_MASTER_PORT))
    if settings.SALT_MASTER_PASS:
        ssh_client.connect(username='root', password=settings.SALT_MASTER_PASS)
    elif settings.SALT_MASTER_KEY:
        sftp_key = paramiko.RSAKey.from_private_key_file(settings.SALT_MASTER_KEY)
        ssh_client.connect(username='root', pkey=sftp_key)
    else:
        ssh_client.connect(username='root')
    sftp_client = paramiko.SFTPClient.from_transport(ssh_client)
    msg = ''
    try:
        sftp_client.stat(remote_dir)
    except IOError as e:
        msg = str(e)
    try:
        if 'No such file' in msg:
            sftp_client.mkdir(remote_dir)
        sftp_client.put(local_file, remote_dir + '/' + filename)
    except Exception as e:
        print(str(e))
    sftp_client.close()
    ssh_client.close()


def Version(dt):
    local_st = utc2local(dt)
    return local_st.strftime('%Y%m%d-%H%M%S')


def _excludes(excludes):
    excludes_cmd = ''

    # 无论是否填写排除.git和.svn, 这两个目录都不会发布
    excludes.append('.git')
    excludes.append('.svn')

    # 去重复
    excludes = list(set(excludes))

    for exclude in excludes:
        if exclude != '':
            excludes_cmd += "--exclude=%s " % exclude

    return excludes_cmd.strip()


def get_files(instance):
    if instance.file_mode == '1':
        return '.'
    elif instance.file_mode == '2':
        files = instance.file_list.split('\n')
        return ' '.join(files)
    else:
        raise AssertionError('files is None')


def _getWorkSpace(instance):
    workspace = os.path.join(settings.SALT_DEPLOY_TEMP, instance.name)
    if not os.path.exists(workspace):
        os.makedirs(workspace, 0o755)
    static_dir = os.path.join(settings.SALT_STATIC, instance.name)
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, 0o755)
    return workspace


def initLocalWorkSpace(instance, task, tasklog=None):
    """初始化宿主机临时空间"""
    workspace = _getWorkSpace(instance)
    git_dir, svn_dir, cmd = None, None, None
    logtext = []
    temp_workspace = os.path.join(workspace, Version(task.created_at))
    if os.path.exists(temp_workspace):
        recode, data = localComannd("rm -rf %s" % temp_workspace)
        if recode == 0:
            print("清理临时目录(%s)成功" % temp_workspace)
        else:
            print("清理临时目录(%s)失败， 原因： %s" % (temp_workspace, str(data)))
        # status, output = subprocess.getstatusoutput("rm -rf %s" % temp_workspace)
    if instance.repo_type == 'git':
        git_dir = os.path.join(instance.repo_work, instance.env, instance.name)
        cmd = ['cp -rf %s %s' % (git_dir, temp_workspace)]
    if instance.repo_type == 'svn':
        svn_dir = os.path.join(instance.repo_work, instance.env, instance.name)
        cmd = ['cp -rf %s %s' % (svn_dir, temp_workspace)]
    command = ' && '.join(cmd)
    print("执行命令： %s" % command)
    recode, data = localComannd(command)
    if recode == 0:
        text = "%s 代码拷贝到 %s 临时空间成功" % (instance.name, workspace)
        print(text)
        message = {'color': 'darkcyan', 'text': text}
        emit_notification(str(task.id), {'message': message})
        logtext.append(message)
        logtext = json.dumps(json.loads(tasklog.log_text) + logtext)
        tasklog.log_text = logtext
        tasklog.save()
    else:
        text = "%s 代码拷贝到 %s 临时空间失败" % (instance.name, workspace)
        print(text)
        print("拷贝临时空间失败原因: %s" % str(data))
        message = {'color': 'red', 'text': text}
        emit_notification(str(task.id), {'message': message})
        emit_notification(str(task.id), {'message': 'end'})
        logtext.append(message)
        task.status = 'failed'
        task.save()
        logtext = json.dumps(json.loads(tasklog.log_text) + logtext)
        tasklog.log_text = logtext
        tasklog.save()
        raise AssertionError(message)


def packageFile(instance, task, tasklog=None):
    """部署资源打包"""
    excludes = instance.repo_ignore.split('\n')
    workspace = _getWorkSpace(instance)
    temp_workspace = os.path.join(workspace, Version(task.created_at))
    package_name = ''.join([temp_workspace, datetime.now().strftime('%Y%m%d-%H%M%S'), '-', task.version, '.tar.gz'])
    files = get_files(task)
    logtext = []
    cmd = ["cd %s" % temp_workspace, "tar -p %s -cz -f %s %s" % (_excludes(excludes), package_name, files)]
    command = ' && '.join(cmd)
    print("执行命令： %s" % command)
    recode, data = localComannd(cmd=command)
    if recode == 0:
        text = "%s 打包到 %s 成功" % (package_name, workspace)
        print(text)
        message = {'color': 'darkcyan', 'text': text}
        emit_notification(str(task.id), {'message': message})
        logtext.append(message)
        logtext = json.dumps(json.loads(tasklog.log_text) + logtext)
        tasklog.log_text = logtext
        tasklog.save()
        return package_name
    else:
        text = "%s 打包到 %s 失败" % (package_name, workspace)
        print(text)
        message = {'color': 'red', 'text': text}
        emit_notification(str(task.id), {'message': message})
        logtext.append(message)
        emit_notification(str(task.id), {'message': 'end'})
        print("打包失败原因： %s" % str(data))
        task.status = 'failed'
        task.save()
        logtext = json.dumps(json.loads(tasklog.log_text) + logtext)
        tasklog.log_text = logtext
        tasklog.save()
        raise AssertionError(text)


def copyPackage(instance, task, package_name, tasklog=None):
    """拷贝部署包到静态资源目录"""
    static_dir = os.path.join(settings.SALT_STATIC, instance.name)
    logtext = []
    cmd = ['cp -rf %s %s' % (package_name, static_dir)]
    command = ' && '.join(cmd)
    print("执行命令： %s" % command)
    recode, data = localComannd(command)
    if recode == 0:
        text = "拷贝(%s)部署包到(%s)静态资源目录成功" % (package_name, 'static')
        message = {'color': 'darkcyan', 'text': text}
        emit_notification(str(task.id), {'message': message})
        logtext.append(message)
        logtext = json.dumps(json.loads(tasklog.log_text) + logtext)
        tasklog.log_text = logtext
        tasklog.save()
    else:
        text = "拷贝(%s)部署包到(%s)静态资源目录失败" % (package_name, 'static')
        message = {'color': 'red', 'text': text}
        emit_notification(str(task.id), {'message': message})
        emit_notification(str(task.id), {'message': 'end'})
        logtext.append(message)
        print("拷贝部署包到静态资源目录失败原因： %s" % str(data))
        task.status = 'failed'
        task.save()
        logtext = json.dumps(json.loads(tasklog.log_text) + logtext)
        tasklog.log_text = logtext
        tasklog.save()
        raise AssertionError(message)
