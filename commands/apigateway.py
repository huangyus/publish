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

from apigateway.models import Upstreams, APIGateWay, GlobalConfig, Vhosts, Maps
from apigateway.utils import build_file
from commands.command import SSHCommand, SFTPCommand, localComannd
from main.models import Middlewares


def generate_pillar(nginx, instance, deploy_type):
    if deploy_type == 'globalconfig':
        data = {'nginx_home': nginx.home, 'package': os.path.join(nginx.name, 'nginx.conf'), 'filename': 'nginx.conf',
                'nginx_run': nginx.cmd}
    elif deploy_type == 'vhosts.d':
        if instance.ssl_status:
            data = {'nginx_home': nginx.home, 'package': os.path.join(nginx.name, deploy_type, '%s.conf' % instance.id),
                    'filename': '%s.conf' % instance.id, 'nginx_run': nginx.cmd, 'ssl_status': instance.ssl_status,
                    'ssl_key_file': '%s.key' % instance.id, 'ssl_cert_file': '%s.cert' % instance.id,
                    'ssl_key_package': os.path.join(nginx.name, 'certs', '%s.key' % instance.id),
                    'ssl_cert_package': os.path.join(nginx.name, 'certs', '%s.cert' % instance.id)
                    }
        else:
            data = {'nginx_home': nginx.home, 'package': os.path.join(nginx.name, deploy_type, '%s.conf' % instance.id),
                    'filename': '%s.conf' % instance.id, 'nginx_run': nginx.cmd, 'ssl_status': instance.ssl_status}
    elif deploy_type == 'all':
        data = {'nginx_home': nginx.home, 'package': os.path.join(nginx.name, nginx.name + '.tar.gz'),
                'filename': '%s.tar.gz' % nginx.name, 'nginx_run': nginx.cmd, 'package_dir': nginx.name}
    elif deploy_type == 'maps':
        if instance.desc:
            filename = '%s-%s.conf' % (instance.desc, instance.id)
        else:
            filename = '%s.conf' % instance.id
        data = {'nginx_home': nginx.home, 'package': os.path.join(nginx.name, deploy_type, '%s.conf' % filename),
                'filename': '%s.conf' % instance.id, 'nginx_run': nginx.cmd}
    else:
        data = {'nginx_home': nginx.home, 'package': os.path.join(nginx.name, deploy_type, instance.name + '.conf'),
                'filename': instance.name + '.conf', 'nginx_run': nginx.cmd}
    return json.dumps(data)


def generate_state(layout_id, nginx):
    layout = Middlewares.objects.get(id=layout_id)
    state_file = os.path.join(settings.NGINX_BASE, layout.name + '-' + layout.version.replace('.', '') + '.sls')
    state_path = os.path.join(settings.NGINX_BASE)
    if not os.path.exists(state_path):
        os.makedirs(state_path, 0o755)
    if os.path.exists(state_file):
        os.remove(state_file)
    with open(state_file, 'w') as f:
        content = layout.content.replace('\r\n', '\n')
        f.write(content)
    return state_file, nginx.name + '/' + layout.name + '-' + layout.version.replace('.',
                                                                                     ''), layout.name + '-' + layout.version.replace(
        '.', '') + '.sls'


def generate_file(nginx, instance, deploy_type):
    path = os.path.join(settings.NGINX_BASE, nginx.name, deploy_type)
    if deploy_type == 'globalconfig':
        path = os.path.join(settings.NGINX_BASE, nginx.name)
        filename = 'nginx.conf'
    elif deploy_type == 'vhosts.d':
        filename = '%s.conf' % instance.id
    elif deploy_type == 'maps':
        if instance.desc:
            filename = '%s-%s.conf' % (instance.desc, instance.id)
        else:
            filename = '%s.conf' % instance.id
    else:
        filename = '%s.conf' % instance.name
    if not os.path.exists(path):
        os.makedirs(path)
    build_file(path=path, filename='%s' % filename, text=instance.content)
    # return os.path.join(instance.name, deploy_type, '%s.conf' % instance.name)


def build_all_file(nginx, instance, build_type):
    for item in instance:
        generate_file(nginx, item, build_type)


def build_all_package(nginx):
    workspace = os.path.join(settings.NGINX_BASE, nginx.name)
    package_name = os.path.join(workspace, nginx.name + '.tar.gz')
    if os.path.exists(package_name):
        os.remove(package_name)
    cmd = ["cd %s" % workspace, "tar -cz -f %s *" % package_name]
    command = ' && '.join(cmd)
    print("执行命令： %s" % command)
    recode, data = localComannd(cmd=command)
    if recode == 0:
        text = "%s 打包到 %s 成功" % (package_name, workspace)
        print(text)
        return nginx.name + '.tar.gz'
    else:
        text = "%s 打包到 %s 失败" % (package_name, workspace)
        print(text)
        raise AssertionError(text)


def generate_all_file(apigateway_id):
    apigateway = APIGateWay.objects.get(id=apigateway_id)
    globalconfig = GlobalConfig.objects.filter(apigateway_id=apigateway_id)
    upstreams = Upstreams.objects.filter(apigateway_id=apigateway_id)
    vhosts = Vhosts.objects.filter(apigateway_id=apigateway_id)
    build_all_file(apigateway, globalconfig, build_type='globalconfig')
    build_all_file(apigateway, upstreams, build_type='upstreams')
    build_all_file(apigateway, vhosts, build_type='vhosts.d')


def generate_cmd(nginx, instance, servers, deploy_type):
    tgt = ', '.join(servers)
    if instance.layout != '0' and instance.layout != '':
        local_file, state_file, filename = generate_state(instance.layout_id, nginx)
        SFTPCommand(local_file, '/srv/salt/' + nginx.name, filename)
        pillar = generate_pillar(nginx, instance, deploy_type)
        if len(servers) <= 1:
            cmd = "salt '%s' state.sls %s pillar='%s' --force-color" % (tgt, state_file, pillar)
        else:
            cmd = "salt -L '%s' state.sls %s pillar='%s' --force-color" % (tgt, state_file, pillar)
        print("执行命令: %s" % cmd)
        return cmd
    else:
        custom_command = json.loads(instance.custom_command)
        command = ' && '.join(custom_command)
        sub = {}
        if '${NGINX_HOME}' in command:
            sub['NGINX_HOME'] = nginx.home
        if '${FILENAME}' in command:
            if deploy_type == 'globalconfig':
                filename = 'nginx.conf'
            elif deploy_type == 'all':
                filename = '%s.tar.gz' % instance.name
            else:
                filename = instance.name + '.conf'
            sub['FILENAME'] = filename
        if '${NGINX_RUN}' in command:
            sub['NGINX_RUN'] = nginx.cmd
        t = Template(command)
        command = t.substitute(sub)
        if len(servers) <= 1:
            cmd = "salt '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, command, '{}')
        else:
            cmd = "salt -L '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, command, '{}')
        return cmd


def generate_check(nginx, instance, servers, deploy_type):
    tgt = ', '.join(servers)
    if deploy_type == 'vhosts.d' or deploy_type == 'maps':
        command = 'mv %s/%s/%s.conf /tmp/ && %s -s reload' % (nginx.home, deploy_type, instance.id, nginx.cmd)
    else:
        command = 'mv %s/%s/%s.conf /tmp/ && %s -s reload' % (nginx.home, deploy_type, instance.name, nginx.cmd)
    if len(servers) <= 1:
        cmd = "salt '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, command, '{}')
    else:
        cmd = "salt -L '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, command, '{}')
    return cmd


def apigateway_event(task_id, deploy_type, category_id):
    apigateway = APIGateWay.objects.get(id=task_id)
    servers = json.loads(apigateway.servers)
    out_file = settings.SALT_LOG + '/' + deploy_type + '/%s.log' % task_id
    cmd = ''
    if not os.path.exists(settings.SALT_LOG + '/' + deploy_type):
        os.makedirs(settings.SALT_LOG + '/' + deploy_type, 0o755)
    if deploy_type == 'globalconfig':
        globalconfig = GlobalConfig.objects.get(id=category_id)
        generate_file(apigateway, globalconfig, deploy_type)
        cmd = generate_cmd(apigateway, globalconfig, servers, deploy_type)
    if deploy_type == 'maps':
        maps = Maps.objects.get(id=category_id)
        generate_file(apigateway, maps, deploy_type)
        if not maps.status:
            cmd = generate_check(apigateway, maps, servers, deploy_type)
        else:
            cmd = generate_cmd(apigateway, maps, servers, deploy_type)
    if deploy_type == 'upstreams':
        upstreams = Upstreams.objects.get(id=category_id)
        generate_file(apigateway, upstreams, deploy_type)
        if not upstreams.status:
            cmd = generate_check(apigateway, upstreams, servers, deploy_type)
        else:
            cmd = generate_cmd(apigateway, upstreams, servers, deploy_type)
    if deploy_type == 'vhosts.d':
        vhosts = Vhosts.objects.get(id=category_id)
        generate_file(apigateway, vhosts, deploy_type)
        if not vhosts.status:
            cmd = generate_check(apigateway, vhosts, servers, deploy_type)
        else:
            cmd = generate_cmd(apigateway, vhosts, servers, deploy_type)
    if deploy_type == 'all':
        generate_all_file(task_id)
        build_all_package(apigateway)
        cmd = generate_cmd(apigateway, apigateway, servers, deploy_type)
    print("执行命令： %s" % cmd)
    recode, data = SSHCommand(cmd, out_file)
    with open(out_file, 'a') as f:
        f.write('end\n')
    if recode == 0:
        return True, data
    else:
        return False, data


class Nginx(object):
    def __init__(self, **kwargs):
        self.task_id = str(kwargs['id'])
        self.instance = kwargs['instance']
        self.deploy_type = kwargs['deploy_type']
        self.category_id = kwargs['category_id']
        self.servers = json.loads(self.instance.servers)
        self.logfile = settings.SALT_LOG + '/nginx/%s.log' % self.task_id
        self.params = None
        self.statefile = None
        self.dt = datetime.now().strftime('%Y%m%d%H%M%S')

        if not os.path.exists(settings.SALT_LOG + '/nginx'):
            os.makedirs(settings.SALT_LOG + '/nginx', 0o755)

        if os.path.exists(self.logfile):
            with open(self.logfile, 'r+') as f:
                f.truncate()

        if self.deploy_type == 'globalconfig':
            self.module = GlobalConfig.objects.get(id=self.category_id)
            self.filename = 'nginx.conf'
            self.path = os.path.join(settings.NGINX_BASE, self.instance.name)
        elif self.deploy_type == 'maps':
            self.module = Maps.objects.get(id=self.category_id)
            if self.module.desc:
                self.filename = '%s-%s.conf' % (self.module.desc, self.module.id)
            else:
                self.filename = '%s.conf' % self.module.id
            self.path = os.path.join(settings.NGINX_BASE, self.instance.name, self.deploy_type)
        elif self.deploy_type == 'upstreams':
            self.module = Upstreams.objects.get(id=self.category_id)
            self.filename = '%s.conf' % self.module.name
            self.path = os.path.join(settings.NGINX_BASE, self.instance.name, self.deploy_type)
        elif self.deploy_type == 'vhosts.d':
            self.module = Vhosts.objects.get(id=self.category_id)
            self.filename = '%s.conf' % re.split("[,| ]", self.module.domain)[0]
            self.path = os.path.join(settings.NGINX_BASE, self.instance.name, self.deploy_type)
        elif self.deploy_type == 'all':
            self.path = os.path.join(settings.NGINX_BASE, self.instance.name)

    def local_command(self, cmd):
        return subprocess.getstatusoutput(cmd)

    @staticmethod
    def ssh_command(cmd, logfile):
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
        # self.text = data
        print(stdout, stderr)
        if logfile is not None:
            with open(logfile, 'a') as f:
                f.write(data)
                f.write('end\n')
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
        remote_dir = os.path.join('/srv', 'salt', remote_dir)
        try:
            sftp_client.stat(remote_dir)
        except IOError as e:
            msg = str(e)
        try:
            if 'No such file' in msg:
                cmd = 'mkdir -p %s' % remote_dir
                Nginx.ssh_command(cmd, logfile=None)
                # sftp_client.mkdir(remote_dir)
            sftp_client.put(local_file, remote_dir + '/' + filename)
        except Exception as e:
            print(str(e))
            return False
        else:
            sftp_client.close()
            ssh_client.close()

    def build_file(self, filename=None):
        if filename is not None:
            self.filename = filename
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if not os.path.isfile(os.path.join(self.path, self.filename)):
            os.mknod(os.path.join(self.path, self.filename), mode=0o644)
        else:
            f = open(os.path.join(self.path, self.filename), 'r+')
            f.truncate()
            f.close()
        with open(os.path.join(self.path, self.filename), 'w') as f:
            text = self.module.content.replace('\r\n', '\n')
            f.write(text)
        print("生成%s文件成功" % self.filename)
        return True

    def build_all_file(self):
        globalconfig = GlobalConfig.objects.filter(apigateway_id=self.task_id)
        for item in globalconfig:
            self.path = os.path.join(settings.NGINX_BASE, self.instance.name, 'nginx.conf')
            self.filename = 'nginx.conf'
            self.module = item
            self.build_file()
        upstreams = Upstreams.objects.filter(apigateway_id=self.task_id)
        for item in upstreams:
            self.path = os.path.join(settings.NGINX_BASE, self.instance.name, 'upstreams', '%s.conf' % item.name)
            self.filename = '%s.conf' % item.name
            self.module = item
            self.build_file()
        vhosts = Vhosts.objects.filter(apigateway_id=self.task_id)
        for item in vhosts:
            self.path = os.path.join(settings.NGINX_BASE, self.instance.name, 'vhosts.d', '%s.conf' % item.id)
            self.filename = '%s.conf' % item.id
            self.module = item
            self.build_file()
        maps = Maps.objects.filter(apigateway_id=self.task_id)
        for item in maps:
            self.path = os.path.join(settings.NGINX_BASE, self.instance.name, 'maps', '%s.conf' % item.id)
            self.filename = '%s.conf' % item.id
            self.module = item
            self.build_file()

    def build_all_package(self):
        workspace = os.path.join(settings.NGINX_BASE, self.instance.name)
        package_name = os.path.join(workspace, self.instance.name + '.tar.gz')
        if os.path.exists(package_name):
            os.remove(package_name)
        cmd = ["cd %s" % workspace, "tar -cz -f %s *" % package_name]
        command = ' && '.join(cmd)
        print("执行命令： %s" % command)
        recode, data = self.local_command(cmd=command)
        if recode == 0:
            text = "%s 打包到 %s 成功" % (package_name, workspace)
            print(text)
            return True
        else:
            text = "%s 打包到 %s 失败" % (package_name, workspace)
            print(text)
            return False

    def build_params(self):
        if self.deploy_type == 'globalconfig':
            data = {'nginx_home': self.instance.home, 'package': os.path.join(self.instance.name, 'nginx.conf'),
                    'filename': 'nginx.conf',
                    'nginx_run': self.instance.cmd}
        elif self.deploy_type == 'vhosts.d':
            if self.module.ssl_status:
                data = {'nginx_home': self.instance.home,
                        'package': os.path.join(self.instance.name, self.deploy_type, self.filename),
                        'filename': self.filename, 'nginx_run': self.instance.cmd,
                        'ssl_status': self.module.ssl_status,
                        'ssl_key_file': '%s.key' % self.module.id, 'ssl_cert_file': '%s.cert' % self.module.id,
                        'ssl_key_package': os.path.join(self.instance.name, 'certs', '%s.key' % self.module.id),
                        'ssl_cert_package': os.path.join(self.instance.name, 'certs', '%s.cert' % self.module.id)
                        }
            else:
                data = {'nginx_home': self.instance.home,
                        'package': os.path.join(self.instance.name, self.deploy_type, self.filename),
                        'filename': self.filename, 'nginx_run': self.instance.cmd,
                        'ssl_status': self.module.ssl_status}
        elif self.deploy_type == 'all':
            data = {'nginx_home': self.instance.home,
                    'package': os.path.join(self.instance.name, self.instance.name + '.tar.gz'),
                    'filename': '%s.tar.gz' % self.instance.name, 'nginx_run': self.instance.cmd,
                    'package_dir': self.instance.name}
        elif self.deploy_type == 'maps':
            data = {'nginx_home': self.instance.home,
                    'package': os.path.join(self.instance.name, self.deploy_type, self.filename),
                    'filename': self.filename, 'nginx_run': self.instance.cmd}
        else:
            data = {'nginx_home': self.instance.home,
                    'package': os.path.join(self.instance.name, self.deploy_type, self.filename),
                    'filename': self.filename, 'nginx_run': self.instance.cmd}
        self.params = data
        print("生成参数成功")
        return True

    def build_statesls(self):
        """生成saltstack state.sls 需要的文件"""
        layout = Middlewares.objects.get(id=self.module.layout_id)
        state_file = os.path.join(settings.NGINX_BASE, layout.name + '-' + layout.version.replace('.', '') + '.sls')
        state_path = os.path.join(settings.NGINX_BASE)
        if not os.path.exists(state_path):
            os.makedirs(state_path, 0o755)
        if os.path.exists(state_file):
            os.remove(state_file)
        with open(state_file, 'w') as f:
            content = layout.content.replace('\r\n', '\n')
            f.write(content)

        self.sftp_command(state_file, 'nginx/' + self.instance.name, layout.name + '-' + layout.version.replace('.', '') + '.sls')
        self.statefile = 'nginx/' + self.instance.name + '/' + layout.name + '-' + layout.version.replace('.', '')
        print("生成sls文件成功")
        time.sleep(1)
        return True

    def build_cmd(self):
        tgt = ', '.join(self.servers)
        if self.module.layout != '0' and self.module.layout != '':
            pillar = json.dumps(self.params)
            if len(self.servers) <= 1:
                cmd = "salt '%s' state.sls %s pillar='%s' --force-color" % (tgt, self.statefile, pillar)
            else:
                cmd = "salt -L '%s' state.sls %s pillar='%s' --force-color" % (tgt, self.statefile, pillar)
            return cmd
        else:
            custom_command = json.loads(self.module.custom_command)
            command = ' && '.join(custom_command)
            sub = {}
            if '${NGINX_HOME}' in command:
                sub['NGINX_HOME'] = self.instance.home
            if '${FILENAME}' in command:
                if self.deploy_type == 'globalconfig':
                    filename = 'nginx.conf'
                elif self.deploy_type == 'all':
                    filename = '%s.tar.gz' % self.instance.name
                elif self.deploy_type == 'maps' or self.deploy_type == 'vhosts.d':
                    filename = self.module.id + '.conf'
                else:
                    filename = self.module.name + '.conf'
                sub['FILENAME'] = filename
            if '${NGINX_RUN}' in command:
                sub['NGINX_RUN'] = self.instance.cmd
            t = Template(command)
            command = t.substitute(sub)
            if len(self.servers) <= 1:
                cmd = "salt '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, command, '{}')
            else:
                cmd = "salt -L '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, command, '{}')
            return cmd

    def destory_cmd(self, arg=None):
        tgt = ', '.join(self.servers)
        if arg:
            command = [
                'mv /tmp/%s-%s %s/%s/%s' % (self.filename, self.dt, self.instance.home, self.deploy_type, self.filename),
                '%s' % self.instance.cmd
            ]
        else:
            command = [
                'mv %s/%s/%s /tmp/%s-%s' % (self.instance.home, self.deploy_type, self.filename, self.filename, self.dt),
                '%s' % self.instance.cmd
            ]
        if len(self.servers) <= 1:
            cmd = "salt '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, ' && '.join(command), '{}')
        else:
            cmd = "salt -L '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, ' && '.join(command), '{}')
        return cmd

    def pre_run(self):
        if not self.build_statesls():
            print("生成sls文件失败")
            return False
        if not self.build_params():
            print("生成参数失败")
            return False
        if not self.build_file():
            print("生成nginx相关配置文件失败")
            return False
        if not self.module.status and self.deploy_type in ('maps', 'upstreams', 'vhosts.d'):
            cmd = self.destory_cmd()
            print("执行命令： %s" % cmd)
            return self.ssh_command(cmd, self.logfile)
        return True

    def run(self):
        if self.deploy_type != 'all':
            if not self.pre_run():
                print("初始化环境失败")
                return False
            cmd = self.build_cmd()
            print("执行命令： %s" % cmd)
            return self.ssh_command(cmd, self.logfile)
        else:
            self.build_all_file()
            if not self.build_all_package():
                return False
            cmd = self.build_cmd()
            print("执行命令： %s" % cmd)
            return self.ssh_command(cmd, self.logfile)

    def destory(self):
        cmd = self.destory_cmd()
        print("执行命令： %s" % cmd)
        return self.ssh_command(cmd, self.logfile)

    def redestory(self):
        cmd = self.destory_cmd(arg='redestory')
        print("执行命令： %s" % cmd)
        return self.ssh_command(cmd, self.logfile)

    def rename_cmd(self, old_filename, new_filename, arg=None):
        tgt = ', '.join(self.servers)
        if arg:
            command = [
                'mv /tmp/%s-%s %s/%s/%s' % (old_filename, self.dt, self.instance.home, self.deploy_type, old_filename, ),
                '%s' % self.instance.cmd
            ]
        else:
            command = [
                'mv %s/%s/%s /tmp/%s-%s' % (self.instance.home, self.deploy_type, old_filename, old_filename, self.dt),
                'wget -qP /tmp %s/nginx/%s/%s/%s' % (settings.WEBSITE_STATIC, self.instance.name, self.deploy_type, new_filename),
                'mv /tmp/%s %s/%s/' % (new_filename, self.instance.home, self.deploy_type),
                '%s' % self.instance.cmd
            ]
        if len(self.servers) <= 1:
            cmd = "salt '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, ' && '.join(command), '{}')
        else:
            cmd = "salt -L '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, ' && '.join(command), '{}')
        return cmd

    def rename(self, old_filename, new_filename):
        cmd = self.rename_cmd(old_filename, new_filename)
        print("执行命令： %s" % cmd)
        return self.ssh_command(cmd, self.logfile)

    def undo_rename(self, old_filename, new_filename):
        cmd = self.rename_cmd(old_filename, new_filename)
        print("执行命令： %s" % cmd)
        return self.ssh_command(cmd, self.logfile)

    def check_upstream_depend(self):
        tgt = ', '.join(self.servers)
        command = [
            'if grep -q "%s" %s/%s/*.conf;then exit 1;else exit 0;fi' % (self.module.name, self.instance.home, 'vhosts.d')
        ]
        if len(self.servers) <= 1:
            cmd = "salt '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, ' && '.join(command), '{}')
        else:
            cmd = "salt -L '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, ' && '.join(command), '{}')
        print("执行命令： %s" % cmd)
        return self.ssh_command(cmd, self.logfile)
