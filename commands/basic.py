import json
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime
from string import Template

import paramiko
from django.conf import settings

from commands.command import SFTPCommand, SSHCommand
from main.models import Basic, Middlewares, TaskLog
from api.consumers import emit_notification


def generate_states_file(bc):
    # states_file = settings.SALT_BASE + '/' + settings.SALT_DEPLOY + '/' + bc.layout + '-' + '-'.join(bc.version.split(".")) + '.sls'
    layout = Middlewares.objects.get(name=bc.layout)
    state_file = os.path.join(settings.SALT_DEPLOY_TEMP, layout.name + '-' + layout.version.replace('.', '') + '.sls')
    if os.path.exists(state_file):
        os.remove(state_file)
    with open(state_file, 'w') as f:
        f.write(layout.content)
    return state_file, 'common/' + layout.name + '-' + layout.version.replace('.', ''),  layout.name + '-' + layout.version.replace('.', '') + '.sls'


def basic_event(task_id, deploy_type):
    basic = Basic.objects.get(id=task_id)
    task_log = TaskLog.objects.get(id=basic.log_id) if len(basic.log_id) > 0 else TaskLog()
    logtext = []
    local_file, state_file, filename = generate_states_file(basic)
    basic.status = 'running'
    basic.log_id = task_log.id
    basic.save()
    SFTPCommand(local_file, '/srv/salt/common', filename)
    if state_file:
        message = {'color': 'darkcyan', 'text': '生成states文件成功'}
        emit_notification(task_id, {'message': message})
        logtext.append(message)
        task_log.log_text = json.dumps(logtext)
        task_log.save()
    servers = json.loads(basic.servers)
    tgt = ', '.join(servers)
    pillar = '{}'
    out_file = settings.SALT_LOG + '/' + deploy_type + '/%s.log' % task_id
    if not os.path.exists(settings.SALT_LOG + '/' + deploy_type):
        os.makedirs(settings.SALT_LOG + '/' + deploy_type, 0o755)

    if len(servers) <= 1:
        cmd = "salt '%s' state.sls %s pillar='%s' --force-color" % (tgt, state_file, pillar)
    else:
        cmd = "salt -L '%s' state.sls %s pillar='%s' --force-color" % (tgt, state_file, pillar)
    print("执行命令： %s" % cmd)
    recode = SSHCommand(cmd, out_file)
    with open(out_file, 'a') as f:
        f.write('end\n')
    if recode == 0:
        return True
    else:
        return False


class BasicDeploy(object):
    def __init__(self, **kwargs):
        self.task_id = str(kwargs['id'])
        self.instance = kwargs['instance']
        self.layout = Middlewares.objects.get(name=kwargs['layout'])
        self.task_log = TaskLog.objects.get(id=self.instance.log_id) if len(self.instance.log_id) > 0 else TaskLog()
        self.servers = json.loads(self.instance.servers)
        self.logfile = settings.SALT_LOG + '/bc/%s.log' % self.task_id
        self.logtext = []
        self.command = None
        self.params = None
        self.text = None

        if not os.path.exists(settings.SALT_LOG + '/bc'):
            os.makedirs(settings.SALT_LOG + '/bc', 0o755)
        if not os.path.exists(os.path.join(settings.SALT_DEPLOY_TEMP, 'common')):
            os.makedirs(os.path.join(settings.SALT_DEPLOY_TEMP, 'common'), 0o755)
        if os.path.exists(self.logfile):
            with open(self.logfile, 'r+') as f:
                f.truncate()
        if self.layout.layout_arch == 'bash':
            content = json.loads(self.layout.content)
            self.deploy_delay = int(content['deploy_delay'])

        self.destory(status='running')

    def destory(self, status):
        if status == 'success':
            Basic.objects.filter(project=self.instance.project, version=self.instance.version).exclude(id=self.instance.id).update(current=False)
            self.instance.current = True
        self.instance.status = status
        self.instance.log_id = self.task_log.id
        self.instance.save()
        self.task_log.log_text = json.dumps(self.logtext)
        self.task_log.save()

    def build_params(self):
        params = dict()
        params['component'] = self.instance.component
        params['version'] = self.instance.version
        self.params = params
        return True

    def _emit_notification(self, message):
        emit_notification(self.task_id, message)

    @staticmethod
    def build_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def build_macro(self, command):
        sub = dict()
        if '${component}' in command:
            sub['component'] = self.params['component']
        if '${version}' in command:
            sub['component'] = self.params['component']
        t = Template(command)
        command = t.substitute(sub)
        return command

    def ssh_command(self, cmd, logfile):
        ENV = ['export LANG=zh_CN.UTF-8', 'export LC_CTYPE=zh_CN.UTF-8']
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if settings.SALT_MASTER_PASS:
                ssh_client.connect(settings.SALT_MASTER, username=settings.SALT_MASTER_USER,
                                   password=settings.SALT_MASTER_PASS, port=settings.SALT_MASTER_PORT, timeout=6000)
            elif settings.SALT_MASTER_KEY:
                ssh_key = paramiko.RSAKey.from_private_key_file(settings.SALT_MASTER_KEY)
                ssh_client.connect(settings.SALT_MASTER, username=settings.SALT_MASTER_USER, pkey=ssh_key,
                                   port=settings.SALT_MASTER_PORT, timeout=6000)
            else:
                ssh_client.connect(settings.SALT_MASTER, username=settings.SALT_MASTER_USER,
                                   port=settings.SALT_MASTER_PORT, timeout=6000)
        except (socket.error, paramiko.AuthenticationException, paramiko.SSHException) as message:
            print("ERROR: SSH connection to " + settings.SALT_MASTER + " failed: " + str(message))
            sys.exit(1)
        command = " && ".join(ENV)
        command = command + " && " + cmd
        stdin, stdout, stderr = ssh_client.exec_command(command)
        data = ''.join(stdout.readlines())
        self.text = data
        with open(logfile, 'a') as f:
            f.write(data)
        code = stdout.channel.recv_exit_status()
        if code == 0:
            return True
        else:
            return False

    @staticmethod
    def sftp_command(local_file, remote_dir, filename):
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

    def local_command(self, cmd):
        (recode, data) = subprocess.getstatusoutput(cmd)
        self.text = str(data)
        if recode == 0:
            return True
        else:
            print(data)
            return False

    @staticmethod
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

    def build_color(self):
        detail = []
        for line in self.text.split('\n'):
            detail.append(self.set_color(line))
        return detail

    def send_log(self, server, status):
        detail = self.build_color()
        failed = False if status else True
        if status:
            text = '%s      Success' % server
            message = {'color': 'green', 'text': text, 'detail': detail, 'failed': failed, 'host': server}
        else:
            text = '%s      Failed' % server
            message = {'color': 'red', 'text': text, 'detail': detail, 'failed': failed, 'host': server}
        self.logtext.append(message)
        self._emit_notification({'message': message})

    def pre_run(self):
        if not self.build_params():
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        return True

    def build_bash(self, args=None):
        """生成bash编排内容"""
        command = None
        if self.layout.layout_arch == 'bash':
            content = json.loads(self.layout.content)
            command = content[args].split('\n')
        elif args is None:
            command = self.layout.content.split('\n')
        if len(command) > 2:
            return ' && '.join(command)
        else:
            return ''.join(command)

    def build_cmd(self, servers):
        tgt = ', '.join(servers)
        pillar = json.dumps(self.params)
        if self.layout.layout_arch == 'bash' or self.layout.layout_arch == 'bash_simple':
            if len(servers) <= 1:
                cmd = "salt '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, self.command, '{}')
            else:
                cmd = "salt -L '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, self.command, '{}')
            return cmd
        else:
            if len(servers) <= 1:
                cmd = "salt '%s' state.sls %s pillar='%s' --force-color" % (tgt, self.params['state_file'], pillar)
            else:
                cmd = "salt -L '%s' state.sls %s pillar='%s' --force-color" % (tgt, self.params['state_file'], pillar)
            return cmd

    def bash_simple_run(self):
        """自定义命令发部入口"""
        for server in self.servers:
            self.params['host'] = server
            self._emit_notification({'message': {'color': 'green', 'text': '%s %s 开始部署' % (self.build_time(), server)}})
            command = self.build_bash()
            self.command = self.build_macro(command)
            cmd = self.build_cmd([server])
            print("执行命令： %s" % cmd)
            if not self.ssh_command(cmd, self.logfile):
                self.destory(status='failed')
                self._emit_notification({'message': 'end'})
                return False
            else:
                self.send_log(server, status=True)
            self._emit_notification({'message': {'color': 'green', 'text': '%s %s 部署完成' % (self.build_time(), server)}})
        self.destory(status='success')
        self._emit_notification({'message': 'end'})
        return True

    def deploy_pre(self):
        """自定义命令，发部之前调用"""
        command = self.build_bash(args='deploy_pre')
        self.command = self.build_macro(command)
        print("Bash部署前命令: %s" % self.command)
        if not self.local_command(self.command):
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        return True

    def deploy_release(self, server):
        """自定义命令，发部调用"""
        command = self.build_bash(args='deploy_release')
        self.command = self.build_macro(command)
        cmd = self.build_cmd([server])
        print("Bash部署命令: %s" % cmd)
        if not self.ssh_command(cmd, self.logfile):
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        return True

    def bash_run(self):
        """自定义命令编排发部入口"""
        status = False
        for server in self.servers:
            self._emit_notification({'message': {'color': 'green', 'text': '%s %s 开始部署前任务' % (self.build_time(), server)}})
            if not self.deploy_pre():
                self.destory(status='failed')
                self.send_log(server, status)
                self._emit_notification({'message': 'end'})
                return status
            else:
                self.send_log(server, status=True)
            self._emit_notification({'message': {'color': 'green', 'text': '%s %s 开始部署任务' % (self.build_time(), server)}})
            if not self.deploy_release(server):
                self.destory(status='failed')
                self.send_log(server, status)
                self._emit_notification({'message': 'end'})
                return status
            else:
                self.send_log(server, status=True)
            self._emit_notification({'message': {'color': 'green', 'text': '%s %s 开始部署后任务' % (self.build_time(), server)}})
            if not self.deploy_post(server):
                self.destory(status='failed')
                self.send_log(server, status)
                self._emit_notification({'message': 'end'})
                return status
            else:
                self.send_log(server, status=True)
            if self.deploy_delay != 0:
                self._emit_notification({'message': {'color': 'green', 'text': '%s %s 开始部署等待%s秒' % (self.build_time(), server, self.deploy_delay)}})
                time.sleep(self.deploy_delay)
            self._emit_notification({'message': {'color': 'green', 'text': '%s %s 部署完成' % (self.build_time(), server)}})
        self.destory(status='success')
        status = True
        self._emit_notification({'message': {'color': 'green', 'text': '%s 部署完成' % self.build_time()}})
        self._emit_notification({'message': 'end'})
        return status

    def deploy_post(self, server):
        """自定义命令，发部之后调用"""
        command = self.build_bash(args='deploy_post')
        self.command = self.build_macro(command)
        cmd = self.build_cmd([server])
        print("Bash部署后命令: %s" % cmd)
        if not self.ssh_command(cmd, self.logfile):
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        return True

    def build_saltstack(self):
        """生成saltstack state.sls 需要的文件"""
        state_file = os.path.join(settings.SALT_DEPLOY_TEMP, 'common', self.layout.name + '-' + self.layout.version.replace('.', '') + '.sls')
        if os.path.exists(state_file):
            os.remove(state_file)
        with open(state_file, 'w') as f:
            f.write(self.layout.content)
        self.params['state_file'] = os.path.join('common', self.layout.name + '-' + self.layout.version.replace('.', ''))
        filename = self.layout.name + '-' + self.layout.version.replace('.', '') + '.sls'
        self.sftp_command(local_file=state_file, remote_dir='/srv/salt/' + 'common', filename=filename)
        message = {'color': 'darkcyan', 'text': '%s 生成%s文件成功' % (self.build_time(), filename)}
        self.logtext.append(message)
        self._emit_notification({'message': message})
        return True

    def salt_run(self):
        """salt state 发部并行入口"""
        if not self.build_saltstack():
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        cmd = self.build_cmd(self.servers)
        print("执行命令： %s" % cmd)
        recode = self.ssh_command(cmd, self.logfile)
        if not self.capture_log():
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        if recode:
            self.destory(status='success')
            self._emit_notification({'message': 'end'})
            return recode
        else:
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return recode

    def deploy_run(self):
        """发布入口"""
        if not self.pre_run():
            print("环境初始化失败")
            return False
        if self.layout.layout_arch == 'bash_simple':
            return self.bash_simple_run()
        elif self.layout.layout_arch == 'bash':
            return self.bash_run()
        else:
            return self.salt_run()

    def capture_send(self):
        detail = self.build_color()
        try:
            if re.findall('Failed:\W+\d+', self.text)[0].split(' ')[-1] == '0':
                failed = False
            else:
                failed = True
        except IndexError as e:
            failed = True
        try:
            host = re.findall('\S+\d+.\d+.\d+.\d+\S+:', self.text)[0].split(':')[0].replace('[0;32m', '') \
                .replace('[0;1;31m', '') \
                .replace('[0;31m', '') \
                .replace('[0;0m', '')\
                .replace('[0;36m', '')
        except IndexError as e:
            host = None
        if failed:
            text = '%s      Failed' % host
            message = {'color': 'red', 'text': text, 'detail': detail, 'failed': failed, 'host': host}
        else:
            text = '%s      Success' % host
            message = {'color': 'green', 'text': text, 'detail': detail, 'failed': failed, 'host': host}
        self.logtext.append(message)
        self._emit_notification({'message': message})
        if failed:
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        return True

    def capture_log(self):
        while True:
            if self.text:
                print("命令结果: %s" % self.text)
                content = re.split('(Total run time\S+\W+[0-9.]+\W\S+)', self.text)
                data = []
                for c in content:
                    if 'Total run' in c:
                        data.append(c)
                        self.text = ''.join(data)
                        if not self.capture_send():
                            return False
                        data = []
                    elif c == '\n':
                        pass
                    else:
                        data.append(c)
                if data:
                    self.text = ''.join(data)
                    if not self.capture_send():
                        return False
                return True
            else:
                time.sleep(2)

