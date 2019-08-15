from celery import task
from commands.apigateway import Nginx
from .models import APIGateWay


@task
def deploy_run(task_id, deploy_type, category_id):
    instance = APIGateWay.objects.get(id=task_id)
    kwargs = instance.to_dict()
    kwargs['instance'] = instance
    kwargs['deploy_type'] = deploy_type
    kwargs['category_id'] = category_id
    obj = Nginx(**kwargs)
    return obj.run()
