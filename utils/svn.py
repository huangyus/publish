import datetime
import os
import shutil
import subprocess

import xmltodict
from utils.common import utc2local, get_encryption_key, decrypt_value


def _getSvnWorkspace(instance, sub_path=None):
    if sub_path:
        return instance.repo_work.strip() + '/' + instance.env + '/' + instance.name + '/' + sub_path
    else:
        return instance.repo_work.strip() + '/' + instance.env + '/' + instance.name + '/'


def _getSvnCmd(cmd, instance):
    key = get_encryption_key()
    password = decrypt_value(key, instance.repo_pass.strip())
    return '/usr/bin/env LC_ALL=en_US.UTF-8 %s --username=%s --password=%s --non-interactive --trust-server-cert' % (
        cmd, instance.repo_user.strip(), password)


def updateRepo(branch='trunk', instance=None, refresh=False):
    """更新仓库"""
    dot_svn = _getSvnWorkspace(instance, '.svn/')
    svn_dir = _getSvnWorkspace(instance)
    status = False
    result = ''
    if refresh:
        if os.path.exists(svn_dir):
            shutil.rmtree(svn_dir)

    if os.path.exists(dot_svn):
        if branch != 'trunk':
            cmd = ['cd %s' % svn_dir, _getSvnCmd('svn cleanup', instance), _getSvnCmd('svn revert . -q -R', instance),
                   _getSvnCmd('svn up -r %s -q --force' % branch, instance)]
        else:
            cmd = ['cd %s' % svn_dir, _getSvnCmd('svn cleanup', instance), _getSvnCmd('svn revert . -q -R', instance),
                   _getSvnCmd('svn up -q --force', instance)]
        command = ' && '.join(cmd)
        print("执行命令： %s" % command)
        result += "执行命令： %s\n" % command
        recode, data = subprocess.getstatusoutput(command)
        if recode == 0:
            print("svn 代码拉取成功")
            result += "svn 代码拉取成功\n"
            status = True
        else:
            print("svn 代码拉取失败")
            result += "svn 代码拉取失败\n"
    else:
        if branch != 'trunk':
            cmd = ['mkdir -p %s' % svn_dir, 'cd %s' % svn_dir,
                   _getSvnCmd('svn checkout -r %s -q %s .' % (branch, instance.repo_url), instance)]
        else:
            cmd = ['mkdir -p %s' % svn_dir, 'cd %s' % svn_dir,
                   _getSvnCmd('svn checkout -q %s .' % instance.repo_url, instance)]
        command = ' && '.join(cmd)
        print("执行命令： %s" % command)
        result += "执行命令： %s\n" % command
        recode, data = subprocess.getstatusoutput(command)
        if recode == 0:
            print("svn 代码拉取成功")
            result += "svn 代码拉取成功\n"
            status = True
        else:
            print("svn 代码拉取失败")
            result += "svn 代码拉取失败\n"
    instance.repo_result = result
    instance.status = status
    instance.save()
    return status


def updateToVersion(instance, commit_id=None):
    """更新到指定commit版本"""
    updateRepo(instance=instance)
    svn_dir = _getSvnWorkspace(instance)
    if commit_id is not None:
        cmd = ['cd %s' % svn_dir, _getSvnCmd('svn up -q --force -r %d' % commit_id, instance)]
    else:
        cmd = ['cd %s' % svn_dir, _getSvnCmd('svn up -q --force', instance)]
    command = ' && '.join(cmd)
    recode, data = subprocess.getstatusoutput(command)
    if recode == 0:
        return True
    else:
        return False


def getBranchList(instance):
    updateRepo(instance=instance)
    svn_dir = _getSvnWorkspace(instance)
    branch = []
    if instance.repo_mode == 'branch':
        trunk_dir = '%s/trunk' % svn_dir
        if os.path.exists(trunk_dir):
            branch.append({'id': 'trunck', 'message': 'trunck'})
        else:
            branch.append({'id': '', 'message': 'default no trunk'})
    branch = getTagList(instance)
    return branch


def getCommitList(instance, count=30):
    updateRepo(instance=instance)
    svn_dir = _getSvnWorkspace(instance)
    cmd = ['cd %s' % svn_dir, _getSvnCmd('svn log --xml -l %d' % count, instance)]
    command = ' && '.join(cmd)
    print("执行命令： %s" % command)
    recode, data = subprocess.getstatusoutput(command)
    commit = []
    if recode == 0:
        xml_data = xmltodict.parse(data)
        try:
            first = xml_data['log']['logentry'][0]
            for xml in xml_data['log']['logentry']:
                print(xml)
                local_st = utc2local(datetime.datetime.strptime(xml['date'], '%Y-%m-%dT%H:%M:%S.%fZ'))
                try:
                    commit.append({'id': xml['@revision'], 'date': local_st.strftime('%Y-%m-%d %H:%M:%S'), 'author': xml['author'], 'message': xml['msg'][0:60]})
                except TypeError:
                    commit.append({'id': xml['@revision'], 'date': local_st.strftime('%Y-%m-%d %H:%M:%S'), 'author': xml['author'], 'message': xml['msg']})
        except KeyError as e:
            local_st = utc2local(datetime.datetime.strptime(xml_data['log']['logentry']['date'], '%Y-%m-%dT%H:%M:%S.%fZ'))
            commit.append({'id': xml_data['log']['logentry']['@revision'], 'date': local_st.strftime('%Y-%m-%d %H:%M:%S'), 'author': xml_data['log']['logentry']['author'], 'message': xml_data['log']['logentry']['msg']})
    return commit


def getTagList(instance):
    tag_dir = _getSvnWorkspace(instance, sub_path='tags/')
    tag = [{'id': 'trunk', 'message': 'trunk'}]
    if not os.path.exists(tag_dir) and not updateRepo(instance=instance):
        return tag
    tag = []
    for t in os.scandir(tag_dir):
        if t.is_file():
            continue
        if t.name == '.svn':
            continue
        tag.append({'id': t.name, 'message': t.name})
    tag = sorted(tag, reverse=True)
    return tag
