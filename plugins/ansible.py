import json
import os
import re
import time

from django.conf import settings

from main.models import Middlewares

__author__ = "hankboy"
__email__ = "491041584@qq.com"

from .base import BaseDeploy


class Ansible(BaseDeploy):
    def build_hosts(self, servers):
        hosts_file = os.path.join(settings.SALT_DEPLOY_TEMP, self.instance.modules, 'hosts')
        if os.path.exists(hosts_file):
            os.remove(hosts_file)
        with open(hosts_file, 'w') as f:
            f.write(servers)
        self.params['hosts'] = hosts_file

    def build_cmd(self):
        if self.layout == '0' and not self.cmd_type:
            pass
        if self.layout == '0' and self.cmd_type:
            filename = self.build_cmd_file()
            command = 'wget -qP /tmp %s/custom_cmd/%s && bash /tmp/%s' % (settings.WEBSITE_STATIC, filename, filename)
            cmd = "salt -L '%s' cmd.run '%s' pillar='%s' --force-color" % ('*', command, '{}')
            return cmd
        params = json.dumps(self.params)
        cmd = "ansible-playbook -i %s %s -e '%s'" % (self.params['hosts'], self.params['playbook'], params)
        return cmd

    def build_playbook(self):
        """生成ansible-playbook 需要的文件"""
        layout = Middlewares.objects.get(name=self.instance.layout)
        playbook_file = os.path.join(settings.SALT_DEPLOY_TEMP, self.instance.modules,
                                     layout.name + '-' + layout.version.replace('.', '') + '.yml')
        if os.path.exists(playbook_file):
            os.remove(playbook_file)
        with open(playbook_file, 'w') as f:
            f.write(layout.content)
        self.params['playbook_file'] = playbook_file
        filename = layout.name + '-' + layout.version.replace('.', '') + '.yml'
        message = {'color': 'darkcyan', 'text': '生成%s文件成功' % filename}
        self.logtext.append(message)
        self._emit_notification({'message': message})

    def capture_log(self):
        while True:
            if self.text:
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

    def running(self):
        if self.deploy:
            deploy = self.deploy.split('\n')
            if len(deploy) > 2:
                command = ' && '.join(deploy)
            else:
                command = ''.join(deploy)
            self.command = self.build_macro(command)
            cmd = self.build_cmd()
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
            cmd = self.build_cmd()
            return self.ssh_command(cmd, self.logfile)
        else:
            self._emit_notification({'message': 'end'})
            return False

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
            if not self.running():
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

    def ansible_serial_run(self):
        """ansible playbook 发部串行入口"""
        status = False
        self.build_playbook()
        for server in self.servers:
            self.params['host'] = server
            cmd = self.build_cmd()
            print("执行命令： %s" % cmd)
            if not self.ssh_command(cmd, self.logfile):
                self.destory(status='failed')
                self.send_log(server, status)
                self._emit_notification({'message': 'end'})
                return status
            else:
                self.send_log(server, status=True)
        status = True
        self.destory(status='success')
        self._emit_notification({'message': 'end'})
        return status

    def ansible_run(self):
        """ansible playbook 发部并行入口"""
        self.build_playbook()
        cmd = self.build_cmd()
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
        """部署入口"""
        time.sleep(2)
        if not self.build_env():
            print("环境初始化失败")
            return False
        if self.layout == '0':
            return self.custom_cmd_run()
        elif self.updownline:
            if self.layout == '0':
                return self.custom_cmd_run()
            else:
                return self.ansible_serial_run()
        elif self.serial:
            return self.ansible_serial_run()
        else:
            return self.ansible_run()
