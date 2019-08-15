import time

from celery import task
from celery import signals
from celery import current_app
from django.conf import settings

from api.consumers import emit_notification
from utils import git, svn
from main.models import Modules, Business, Basic
from utils.common import workflow_sendlog
from commands.business import BusinessDeploy
from commands.workflow import Workflow
from commands.basic import BasicDeploy


@task
def add(x, y, sleep=None):
    print("睡眠%d秒" % sleep)
    for i in range(sleep, 0, -1):
        time.sleep(1)
        print("剩余%d秒执行" % i)
    return x + y


def task_success_handler(sender, **kwargs):
    print("task_successs")
    print(kwargs)
    print(kwargs['result'])


def task_postrun_handler(sender=None, task_id=None, task=None, retval=None, state=None, *args, **kwargs):
    task_id = kwargs['args'][0]
    deploy_type = kwargs['args'][1]
    outfile = settings.SALT_LOG + '/' + deploy_type + '/%s.log' % task_id
    print(outfile)
    with open(outfile, 'a') as f:
        f.write('end\n')


@signals.worker_process_init.connect
def on_pool_process_init(**kwargs):
    signals.task_postrun.connect(task_postrun_handler, sender=current_app.tasks[deploy_run.name])


@task
def PullRepo(repo, refresh):
    instance = Modules.objects.get(id=repo)
    if instance.repo_type == 'git':
        status = git.updateRepo(instance=instance, refresh=refresh)
        if status:
            return True
        else:
            return False

    if instance.repo_type == 'svn':
        status = svn.updateRepo(instance=instance, refresh=refresh)
        if status:
            return True
        else:
            return False


@task
def deploy_run(task_id, deploy_type):
    if deploy_type == 'bs':
        business = Business.objects.get(id=task_id)
        kwargs = business.to_dict()
        kwargs['instance'] = business
        kwargs['module'] = Modules.objects.get(name=business.modules, project=business.project)
        bd = BusinessDeploy(**kwargs)
        return bd.deploy_run()
    if deploy_type == 'bc':
        basic = Basic.objects.get(id=task_id)
        kwargs = basic.to_dict()
        kwargs['instance'] = basic
        bc = BasicDeploy(**kwargs)
        return bc.deploy_run()


@task
def workflow_deploylog(deploy_type, **kwargs):
    out_file = settings.SALT_LOG + '/' + deploy_type + '/%s.log' % kwargs['task_id']
    recode = workflow_sendlog(out_file, kwargs['task_id'])
    instance = Business.objects.get(id=kwargs['id'])
    if recode:
        instance.status = 'success'
        emit_notification(kwargs['task_id'], {'message': 'end'})
    else:
        instance.status = 'failed'
        emit_notification(kwargs['task_id'], {'message': 'end'})
    instance.save()
    return recode


@task(queue='workflow')
def workflow_deploy(running, **kwargs):
    if running:
        text = '执行步骤 ' + str(kwargs['idx'])
        print(text)
        message = {'color': 'darkcyan', 'text': '执行步骤 %d' % kwargs['idx']}
        kwargs['logtext'] = [message, ]
        wf = Workflow(**kwargs)
        emit_notification(kwargs['id'], {'message': message})
        return wf.deploy_run()
    return running
