import json
import os
import socket
import subprocess
import sys
import uuid
from string import Template

import paramiko
from django.conf import settings

from api.consumers import emit_notification
from main.models import TaskLog
from utils import git, svn
from utils.common import utc2local


class BaseDeploy(object):
    def __init__(self, **kwargs):
        self.task_id = str(kwargs['id'])
        self.instance = kwargs['instance']
        self.module = kwargs['module']
        self.layout = kwargs['layout']
        self.serial = kwargs['serial']
        self.updownline = kwargs['updownline']
        self.pre_deploy = self.module.pre_deploy
        self.deploy = self.module.deploy
        self.post_deploy = self.module.post_deploy
        self.deploy_delay = self.module.deploy_delay
        self.gateway_type = self.module.arch_type
        self.cmd_type = self.module.cmd_type
        self.task_log = TaskLog.objects.get(id=self.instance.log_id) if len(self.instance.log_id) > 0 else TaskLog()
        self.servers = json.loads(self.instance.servers)
        self.logfile = settings.SALT_LOG + '/bs/%s.log' % self.task_id
        self.logtext = []
        self.params = None
        self.command = None
        self.text = None
        self.cmd_file = None

        if not os.path.exists(settings.SALT_LOG + '/bs'):
            os.makedirs(settings.SALT_LOG + '/bs', 0o755)
        if not os.path.exists(os.path.join(settings.SALT_DEPLOY_TEMP, self.instance.modules)):
            os.makedirs(os.path.join(settings.SALT_DEPLOY_TEMP, self.instance.modules), 0o755)
        if os.path.exists(self.logfile):
            with open(self.logfile, 'r+') as f:
                f.truncate()
        self.destory(status='running')

    def destory(self, status):
        self.instance.status = status
        self.instance.log_id = self.task_log.id
        self.instance.save()
        self.task_log.log_text = json.dumps(self.logtext)
        self.task_log.save()

    def _get_workspace(self):
        workspace = os.path.join(settings.SALT_DEPLOY_TEMP, self.instance.name)
        if not os.path.exists(workspace):
            os.makedirs(workspace, 0o755)
        static_dir = os.path.join(settings.SALT_STATIC, 'deploy')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir, 0o755)
        return workspace

    def _get_version(self):
        local_st = utc2local(self.instance.created_at)
        return local_st.strftime('%Y%m%d%H%M%S')

    def _get_getfile(self):
        if self.instance.file_mode == '1':
            return '.'
        else:
            files = self.instance.file_list.split('\n')
            return ' '.join(files)

    @staticmethod
    def _get_excludes(excludes):
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
            status = git.updateRepo(branch=self.instance.version, instance=self.module)
        else:
            status = svn.updateRepo(branch=self.instance.version, instance=self.module)

        if status:
            self.module.status = status
            self.module.save()
            message = {'color': 'darkcyan', 'text': '%s 切换到 %s 版本成功' % (self.module.repo_type, self.instance.version)}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            self.task_log.log_text = json.dumps(self.logtext)
            self.task_log.save()
            return True
        else:
            message = {'color': 'darkcyan', 'text': '%s 切换到 %s 版本失败' % (self.module.repo_type, self.instance.version)}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            self._emit_notification({'message': 'end'})
            self.task_log.log_text = json.dumps(self.logtext)
            self.task_log.save()
            self.instance.status = 'failed'
            self.instance.save()
            return False

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
            text = "%s 代码拷贝到 %s 临时空间成功" % (self.module.name, self.params['workspace'])
            print(text)
            message = {'color': 'darkcyan', 'text': text}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            return recode
        else:
            text = "%s 代码拷贝到 %s 临时空间失败" % (self.module.name, self.params['workspace'])
            print(text)
            message = {'color': 'red', 'text': text}
            self._emit_notification({'message': message})
            self._emit_notification({'message': 'end'})
            self.logtext.append(message)
            return recode

    def build_package(self):
        """部署资源打包"""
        excludes = self.module.repo_ignore.split('\n')
        package_name = ''.join([self.params['temp_workspace'], '-', self.instance.version, '.tar.gz'])
        cmd = ["cd %s" % self.params['temp_workspace'], "tar -p %s -cz -f %s %s" % (self._get_excludes(excludes), package_name, self._get_getfile())]
        command = ' && '.join(cmd)
        print("执行命令： %s" % command)
        recode = self.local_command(command)
        if recode:
            text = "%s 打包到 %s 成功" % (package_name, self.params['workspace'])
            print(text)
            message = {'color': 'darkcyan', 'text': text}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            return recode
        else:
            text = "%s 打包到 %s 失败" % (package_name, self.params['workspace'])
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
        cmd = ['cp -rf %s %s' % (''.join([self.params['temp_workspace'], '-', self.instance.version, '.tar.gz']), static_dir)]
        command = ' && '.join(cmd)
        print("执行命令： %s" % command)
        recode = self.local_command(command)
        if recode:
            text = "拷贝(%s)部署包到(%s)静态资源目录成功" % (self.params['package_name'], 'static')
            message = {'color': 'darkcyan', 'text': text}
            self._emit_notification({'message': message})
            self.logtext.append(message)
            return recode
        else:
            text = "拷贝(%s)部署包到(%s)静态资源目录失败" % (self.params['package_name'], 'static')
            message = {'color': 'red', 'text': text}
            self._emit_notification({'message': message})
            self._emit_notification({'message': 'end'})
            self.logtext.append(message)
            return recode

    def build_params(self):
        params = dict()
        params['workspace'] = self._get_workspace()
        params['version'] = self._get_version()
        params['package_name'] = params['version'] + '-' + self.instance.version + '.tar.gz'
        params['package'] = 'deploy/' + params['package_name']
        params['temp_workspace'] = os.path.join(params['workspace'], params['version'])
        params['deploy_project'] = self.module.dest_repo.rstrip('/') + '/' + self.instance.project + '_' + self.module.name + '/' + params['version'] + '-' + self.instance.version
        params['deploy_root'] = self.module.dest_root
        params['module_name'] = self.instance.project + '_' + self.instance.modules
        self.params = params

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

    def pre_run(self):
        """自定义命令，发部之前调用"""
        pass

    def running(self, server):
        """自定义命令，发部调用"""
        pass

    def post_run(self, server):
        """自定义命令，发部之后调用"""
        pass

    def build_env(self):
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

    def build_cmd_file(self):
        filename = '%s.sh' % str(uuid.uuid1())
        if not os.path.exists(os.path.join(settings.SALT_STATIC, 'custom_cmd')):
            os.makedirs(os.path.join(settings.SALT_STATIC, 'custom_cmd'))
        with open(os.path.join(settings.SALT_STATIC, 'custom_cmd', filename), 'w') as f:
            f.write(self.command)
        return filename

    def build_cmd(self, servers):
        """生成发部命令"""
        pass

    def custom_cmd_run(self):
        """自定义命令发部入口"""
        pass

    @staticmethod
    def set_color(line):
        """给日志添加网页颜色"""
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
        """部署日志转成网页格式"""

    def capture_log(self):
        """收集部署的日志"""
        pass

    def capture_send(self):
        """发送部署的日志给前端展示"""
        pass

    def send_log(self, server, status):
        """发送自定义命令的日志给前端展示"""
        pass

    def deploy(self):
        """部署入口"""
        pass
