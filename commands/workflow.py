import json
import os
import re
import socket
import subprocess
import sys
import time
import uuid
from datetime import datetime
from string import Template

import paramiko

from api.consumers import emit_notification
from publish import settings
from utils import git, svn
from main.models import WorkFlow, Modules, Middlewares, TaskLog
from utils.common import utc2local


class Workflow(object):
    def __init__(self, **kwargs):
        self.step = kwargs['idx']
        self.task_id = kwargs['id']
        self.instance = WorkFlow.objects.get(id=kwargs['id'])
        self.project = kwargs['project']
        self.servers = kwargs['servers']
        self.version = kwargs['version']
        self.created_at = kwargs['created_at']
        self.serial = kwargs['serial']
        self.updownline = kwargs['updownline']
        self.layout = kwargs['layout']
        self.custom_command = kwargs.get('custom_command', None)
        self.package = None
        self.statefile = None
        self.pillar = '{}'
        self.cmd = None
        self.outfile = None
        self.module = Modules.objects.get(name=kwargs['modules'])
        self.cmd_type = self.module.cmd_type
        self.pre_deploy = self.module.pre_deploy
        self.deploy = self.module.deploy
        self.post_deploy = self.module.post_deploy
        self.deploy_delay = self.module.deploy_delay
        self.task_log = TaskLog.objects.get(id=self.instance.log_id) if len(self.instance.log_id) > 0 else TaskLog()
        self.logfile = settings.SALT_LOG + '/workflow/%s.log' % self.task_id
        self.text = None
        self.logtext = kwargs.get('logtext', None) or []
        self.params = None
        self.command = None
        self.cmd_file = None

        if not os.path.exists(settings.SALT_LOG + '/' + 'workflow'):
            os.makedirs(settings.SALT_LOG + '/' + 'workflow', 0o755)
        if not os.path.exists(os.path.join(settings.SALT_DEPLOY_TEMP, self.module.name)):
            os.makedirs(os.path.join(settings.SALT_DEPLOY_TEMP, self.module.name), 0o755)

    @staticmethod
    def build_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _generate_workspace(self):
        workspace = os.path.join(settings.SALT_DEPLOY_TEMP, self.module.name)
        if not os.path.exists(workspace):
            os.makedirs(workspace, 0o755)
        static_dir = os.path.join(settings.SALT_STATIC, 'deploy')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir, 0o755)
        return workspace

    def _generate_version(self):
        local_st = utc2local(self.created_at)
        return local_st.strftime('%Y%m%d%H%M%S')

    def _getfile(self):
        return '.'
        # if self.instance.file_mode == '1':
        #     return '.'
        # else:
        #     files = self.instance.file_list.split('\n')
        #     return ' '.join(files)

    def _excludes(self, excludes):
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

    def _emit_notification(self, message):
        emit_notification(self.task_id, message)

    def local_command(self, cmd):
        (recode, data) = subprocess.getstatusoutput(cmd)
        self.text = str(data)
        if recode == 0:
            return True
        else:
            return False

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

    def build_repo(self):
        if self.module.repo_type == 'git':
            status = git.updateRepo(branch=self.version, instance=self.module)
        else:
            status = svn.updateRepo(branch=self.version, instance=self.module)

        if status:
            self.module.status = status
            self.module.save()
            message = {'color': 'darkcyan', 'text': '%s %s 切换到 %s 版本成功' % (self.build_time(), self.module.repo_type, self.version)}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            return True
        else:
            message = {'color': 'darkcyan', 'text': '%s %s 切换到 %s 版本失败' % (self.build_time(), self.module.repo_type, self.version)}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            self._emit_notification({'message': 'end'})
            return False

    def build_params(self):
        params = dict()
        params['workspace'] = self._generate_workspace()
        params['version'] = self.created_at
        params['package_name'] = params['version'] + '-' + self.version + '.tar.gz'
        params['package'] = 'deploy/' + params['package_name']
        params['temp_workspace'] = os.path.join(params['workspace'], params['version'])
        params['deploy_project'] = self.module.dest_repo.rstrip(
            '/') + '/' + self.project + '_' + self.module.name + '/' + params[
                                       'version'] + '-' + self.version
        params['deploy_root'] = self.module.dest_root
        params['module_name'] = self.project + '_' + self.module.name
        self.params = params

    def build_workspace(self):
        """初始化宿主机临时空间"""
        git_dir, svn_dir, cmd = None, None, None
        if os.path.exists(self.params['temp_workspace']):
            recode = self.local_command("rm -rf %s" % self.params['temp_workspace'])
            if recode:
                print("清理临时目录(%s)成功" % self.params['temp_workspace'])
            else:
                print("清理临时目录(%s)失败" % self.params['temp_workspace'])
        if self.module.repo_type == 'git':
            git_dir = os.path.join(self.module.repo_work, self.module.env, self.module.name)
            cmd = ['cp -rf %s %s' % (git_dir, self.params['temp_workspace'])]
        if self.module.repo_type == 'svn':
            svn_dir = os.path.join(self.module.repo_work, self.module.env, self.module.name)
            cmd = ['cp -rf %s %s' % (svn_dir, self.params['temp_workspace'])]
        command = ' && '.join(cmd)
        print("执行命令： %s" % command)
        recode = self.local_command(command)
        if recode:
            text = "%s %s 代码拷贝到 %s 临时空间成功" % (self.build_time(), self.module.name, self.params['workspace'])
            print(text)
            message = {'color': 'darkcyan', 'text': text}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            return recode
        else:
            text = "%s %s 代码拷贝到 %s 临时空间失败" % (self.build_time(), self.module.name, self.params['workspace'])
            print(text)
            message = {'color': 'red', 'text': text}
            self._emit_notification({'message': message})
            self._emit_notification({'message': 'end'})
            self.logtext.append(message)
            return recode

    def build_package(self):
        """部署资源打包"""
        excludes = self.module.repo_ignore.split('\n')
        package_name = ''.join([self.params['temp_workspace'], '-', self.version, '.tar.gz'])
        cmd = ["cd %s" % self.params['temp_workspace'],
               "tar -p %s -cz -f %s %s" % (self._excludes(excludes), package_name, self._getfile())]
        command = ' && '.join(cmd)
        print("执行命令： %s" % command)
        recode = self.local_command(command)
        if recode:
            text = "%s %s 打包到 %s 成功" % (self.build_time(), package_name, self.params['workspace'])
            print(text)
            message = {'color': 'darkcyan', 'text': text}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            return recode
        else:
            text = "%s %s 打包到 %s 失败" % (self.build_time(), package_name, self.params['workspace'])
            print(text)
            message = {'color': 'red', 'text': text}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            return recode

    def build_copypackage(self):
        """拷贝部署包到静态资源目录"""
        static_dir = os.path.join(settings.SALT_STATIC, 'deploy')
        package_file = static_dir + '/' + self.params['package_name']
        if os.path.exists(package_file):
            os.remove(package_file)
        cmd = ['cp -rf %s %s' % (''.join([self.params['temp_workspace'], '-', self.version, '.tar.gz']), static_dir)]
        command = ' && '.join(cmd)
        print("执行命令： %s" % command)
        recode = self.local_command(command)
        if recode:
            text = "%s 拷贝(%s)部署包到(%s)静态资源目录成功" % (self.build_time(), self.params['package_name'], 'static')
            message = {'color': 'darkcyan', 'text': text}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            return recode
        else:
            text = "%s 拷贝(%s)部署包到(%s)静态资源目录失败" % (self.build_time(), self.params['package_name'], 'static')
            message = {'color': 'red', 'text': text}
            self._emit_notification({'message': message})
            self._emit_notification({'message': 'end'})
            self.logtext.append(message)
            return recode

    def build_statesls(self):
        """生成saltstack state.sls 需要的文件"""
        layout = Middlewares.objects.get(name=self.layout)
        state_file = os.path.join(settings.SALT_DEPLOY_TEMP, self.module.name,
                                  layout.name + '-' + layout.version.replace('.', '') + '.sls')
        if os.path.exists(state_file):
            os.remove(state_file)
        with open(state_file, 'w') as f:
            f.write(layout.content)
        self.params['state_file'] = os.path.join(self.module.name,
                                                 layout.name + '-' + layout.version.replace('.', ''))
        filename = layout.name + '-' + layout.version.replace('.', '') + '.sls'
        self.sftp_command(local_file=state_file, remote_dir='/srv/salt/' + self.module.name, filename=filename)
        message = {'color': 'darkcyan', 'text': '%s 生成%s文件成功' % (self.build_time(), filename)}
        self._emit_notification({'message': message})

    def build_macro(self, command):
        sub = dict()
        if '${DEPLOYWORKSPACE}' in command:
            sub['DEPLOYWORKSPACE'] = self.params['workspace']
        if '${DEPLOYPACKAGE}' in command:
            sub['DEPLOYPACKAGE'] = self.params['package']
        if '${DEPLOYPACKAGENAME}' in command:
            sub['DEPLOYPACKAGENAME'] = self.params['package_name']
        if '${DEPLOYHOST}' in command:
            sub['DEPLOYHOST'] = self.params['host']
        if '${DEPLOYPROJECT}' in command:
            sub['DEPLOYPROJECT'] = self.params['deploy_project']
        if '${DEPLOYROOT}' in command:
            sub['DEPLOYROOT'] = self.params['deploy_root']
        if '${DEPLOYMODULE}' in command:
            sub['DEPLOYMODULE'] = self.params['module_name']
        t = Template(command)
        command = t.substitute(sub)
        return command

    def build_cmd_file(self):
        filename = '%s.sh' % str(uuid.uuid1())
        if not os.path.exists(os.path.join(settings.SALT_STATIC, 'custom_cmd')):
            os.makedirs(os.path.join(settings.SALT_STATIC, 'custom_cmd'))
        with open(os.path.join(settings.SALT_STATIC, 'custom_cmd', filename), 'w') as f:
            f.write(self.command)
        return filename

    def build_cmd(self, servers):
        tgt = ', '.join(servers)
        if self.layout == '0' and not self.cmd_type:
            if len(servers) <= 1:
                cmd = "salt '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, self.command, '{}')
            else:
                cmd = "salt -L '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, self.command, '{}')
            return cmd
        if self.layout == '0' and self.cmd_type:
            filename = self.build_cmd_file()
            command = 'wget -qP /tmp %s/custom_cmd/%s && bash /tmp/%s' % (settings.WEBSITE_STATIC, filename, filename)
            if len(servers) <= 1:
                cmd = "salt '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, command, '{}')
            else:
                cmd = "salt -L '%s' cmd.run '%s' pillar='%s' --force-color" % (tgt, command, '{}')
            return cmd
        pillar = json.dumps(self.params)
        if len(servers) <= 1:
            cmd = "salt '%s' state.sls %s pillar='%s' --force-color" % (tgt, self.params['state_file'], pillar)
        else:
            cmd = "salt -L '%s' state.sls %s pillar='%s' --force-color" % (tgt, self.params['state_file'], pillar)
        return cmd

    def pre_run(self):
        """自定义命令，发部之前调用"""
        if self.pre_deploy:
            pre_deploy = self.pre_deploy.split('\n')
            if len(pre_deploy) > 2:
                command = ' && '.join(pre_deploy)
            else:
                command = ''.join(pre_deploy)
            self.command = self.build_macro(command)
            if self.cmd_type:
                filename = self.build_cmd_file()
                cmd = 'bash %s/custom_cmd/%s' % (settings.SALT_STATIC, filename)
                return self.local_command(cmd)
            return self.local_command(self.command)
        else:
            self._emit_notification({'message': 'end'})
            return False

    def run(self, server):
        """自定义命令，发部调用"""
        if self.deploy:
            deploy = self.deploy.split('\n')
            if len(deploy) > 2:
                command = ' && '.join(deploy)
            else:
                command = ''.join(deploy)
            self.command = self.build_macro(command)
            cmd = self.build_cmd([server])
            return self.ssh_command(cmd, self.logfile)
        else:
            self._emit_notification({'message': 'end'})
            return False

    def post_run(self, server):
        """自定义命令，发部之后调用"""
        if self.post_deploy:
            post_deploy = self.post_deploy.split('\n')
            if len(post_deploy) > 2:
                command = ' && '.join(post_deploy)
            else:
                command = ''.join(post_deploy)
            self.command = self.build_macro(command)
            cmd = self.build_cmd([server])
            return self.ssh_command(cmd, self.logfile)
        else:
            self._emit_notification({'message': 'end'})
            return False

    def pre_deploy_run(self):
        """发部之前的准备环境"""
        self.build_params()
        if not self.build_repo():
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        if not self.build_workspace():
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        if not self.build_package():
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        if not self.build_copypackage():
            self.destory(status='failed')
            self._emit_notification({'message': 'end'})
            return False
        return True

    def custom_cmd_run(self):
        """自定义命令发部入口"""
        status = False
        for server in self.servers:
            if not self.pre_run():
                self.destory(status='failed')
                self.send_log(server, status)
                self._emit_notification({'message': 'end'})
                return status
            else:
                self.send_log(server, status=True)
            if not self.run(server):
                self.destory(status='failed')
                self.send_log(server, status)
                self._emit_notification({'message': 'end'})
                return status
            else:
                self.send_log(server, status=True)
            if not self.post_run(server):
                self.destory(status='failed')
                self.send_log(server, status)
                self._emit_notification({'message': 'end'})
                return status
            else:
                self.send_log(server, status=True)
            if self.deploy_delay != 0:
                time.sleep(self.deploy_delay)
        self.destory(status='success')
        status = True
        self._emit_notification({'message': 'end'})
        return status

    def SaltState_serial_run(self):
        """salt state 发部串行入口"""
        status = False
        self.build_statesls()
        for server in self.servers:
            self.params['host'] = server
            # if self.module.arch_type == 'nginx_gateway' and self.updownline:
            #     if not self.build_nginx_gateway(server, online='down'):
            #         self.destory(status='failed')
            #         self._emit_notification({'message': 'end'})
            #         return False
            cmd = self.build_cmd([server])
            print("执行命令： %s" % cmd)
            if not self.ssh_command(cmd, self.logfile):
                self.destory(status='failed')
                self.send_log(server, status)
                self._emit_notification({'message': 'end'})
                return status
            else:
                self.send_log(server, status=True)
            # if self.module.arch_type == 'nginx_gateway' and self.updownline:
            #     if not self.build_nginx_gateway(server, online='up'):
            #         return False
        status = True
        self.destory(status='success')
        self._emit_notification({'message': 'end'})
        return status

    def SaltState_run(self):
        """salt state 发部并行入口"""
        self.build_statesls()
        cmd = self.build_cmd(self.servers)
        print("执行命令： %s" % cmd)
        recode = self.ssh_command(cmd, self.logfile)
        if not self.capture_log():
            # self.destory(status='failed')
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
        """发部入口"""
        if not self.pre_deploy_run():
            return False
        if self.layout == '0':
            return self.custom_cmd_run()
        elif self.updownline:
            if self.layout == '0':
                return self.custom_cmd_run()
            else:
                return self.SaltState_serial_run()
        elif self.serial:
            return self.SaltState_serial_run()
        else:
            return self.SaltState_run()

    def build_steps(self, status):
        self.instance.steps = json.loads(self.instance.steps)
        if status == 'success':
            s = 'success'
        else:
            s = 'error'
        for step in self.instance.steps:
            if step['idx'] == self.step:
                step['status'] = s
        self.instance.steps = json.dumps(self.instance.steps)
        self.instance.save()

    def destory(self, status):
        self.instance.status = status
        self.build_steps(status)
        self.instance.log_id = self.task_log.id
        self.instance.save()
        if self.task_log.log_text:
            history_log = json.loads(self.task_log.log_text)
            self.task_log.log_text = json.dumps(history_log + self.logtext)
        else:
            self.task_log.log_text = json.dumps(self.logtext)
        self.task_log.save()

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
                .replace('[0;0m', '') \
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
