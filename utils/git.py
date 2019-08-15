import os
import re
import shutil
import subprocess

from utils.common import decrypt_value, get_encryption_key


def _getGitWorkspace(instance, sub_path=None):
    if sub_path:
        return instance.repo_work.strip() + '/' + instance.env + '/' + instance.name + '/' + sub_path
    else:
        return instance.repo_work.strip() + '/' + instance.env + '/' + instance.name + '/'


def updateRepo(branch='master', instance=None, refresh=False):
    git_dir = _getGitWorkspace(instance)
    status = False
    result = ''
    if refresh:
        if os.path.exists(git_dir):
            shutil.rmtree(git_dir)

    if instance.repo_user and instance.repo_pass:
        credential = instance.repo_url.split("//")
        key = get_encryption_key()
        password = decrypt_value(key, instance.repo_pass.strip())
        repo_url = credential[0] + '//' + instance.repo_user + ':' + password + '@' + credential[1]
    else:
        repo_url = instance.repo_url
    if os.path.exists(git_dir):
        cmd = ['cd %s' % git_dir, 'git checkout -q %s' % branch, 'git fetch -p -q --all', 'git reset -q --hard origin/%s' % branch]
        command = ' && '.join(cmd)
        print("执行命令： %s" % command)
        result += "执行命令： %s\n" % command
        recode, data = subprocess.getstatusoutput(command)
        if recode == 0:
            print("git 代码拉取成功")
            result += "git 代码拉取成功\n"
            status = True
        else:
            print("git 代码拉取失败")
            result += "git 代码拉取失败: %s\n" % data
    else:
        cmd = ['mkdir -p %s' % git_dir, 'cd %s' % git_dir, 'git clone %s .' % repo_url, 'git checkout -q %s' % branch]
        command = ' && '.join(cmd)
        print("执行命令： %s" % command)
        result += "执行命令： %s\n" % command
        recode, data = subprocess.getstatusoutput(command)
        if recode == 0:
            print("git 代码拉取成功")
            result += "git 代码拉取成功\n"
            status = True
        else:
            print("git 代码拉取失败")
            result += "git 代码拉取失败: %s\n" % data
    instance.repo_result = result
    instance.status = status
    instance.save()
    return status


def updateToVersion(instance, commit_id=None):
    updateRepo(instance=instance)
    git_dir = _getGitWorkspace(instance)
    if commit_id is not None:
        cmd = ['cd %s' % git_dir, 'git reset -q --hard %d' % commit_id]
    else:
        cmd = ['cd %s' % git_dir, 'git reset -q']
    command = ' && '.join(cmd)
    recode, data = subprocess.getstatusoutput(command)
    if recode == 0:
        return True
    else:
        return False


def getBranchList(instance):
    updateRepo(instance=instance)
    git_dir = _getGitWorkspace(instance)
    cmd = ['cd %s' % git_dir, 'git fetch -p', 'git pull -a', 'git branch -a']
    command = ' && '.join(cmd)
    branch = []
    recode, data = subprocess.getstatusoutput(command)
    if recode == 0:
        for i in data.split('\n'):
            remote_prefix = 'remotes/origin/'
            remote_head_prefix = 'remotes/origin/HEAD'
            if re.match(remote_prefix, i.strip()) and i.strip()[:len(remote_head_prefix)] != remote_head_prefix:
                branch.append({'id': i.strip()[len(remote_prefix):], 'message': i.strip()[len(remote_prefix):]})
    return branch


def gitCommitList(instance, count=20):
    updateRepo(instance=instance)
    git_dir = _getGitWorkspace(instance)
    cmd = ['cd %s' % git_dir, 'git log -%s --pretty=format:"%%h - %%ad - %%an %%s " --date=local' % count]
    command = ' && '.join(cmd)
    commit = []
    recode, data = subprocess.getstatusoutput(command)
    if recode == 0:
        for i in data.split('\n'):
            commit.append({'id': i.split('-')[0], 'message': i})
    return commit


def gitTagList(instance):
    updateRepo(instance=instance)
    git_dir = _getGitWorkspace(instance)
    cmd = ['cd %s' % git_dir, 'git tag -l']
    command = ' && '.join(cmd)
    tag = []
    recode, data = subprocess.getstatusoutput(command)
    if recode == 0:
        for i in data.split('\n'):
            tag.append({'id': i, 'message': i})
    return tag
