import argparse
import json
from datetime import datetime
import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'publish.settings')
django.setup()
from commands.autodeploy import AutoDeploy
from main.models import Business, Modules


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='自动发布命令行')
    parser.add_argument('-P', metavar='project', type=str, help="项目名称")
    parser.add_argument('-M', metavar='module', type=str, help="模块名称")
    parser.add_argument('-S', metavar='servers', nargs='+', help='服务器列表')
    if len(sys.argv) > 1:
        args = parser.parse_args()
        print(args)
        instance = Business.objects.get(project=args.P, modules=args.M, status='success', current=True)
        if instance:
            obj = Business()
            obj.name = '%s-%s-%s' % (datetime.now().strftime('%Y%m%d%H%M%S'), args.P, args.M)
            obj.project = args.P
            obj.modules = args.M
            obj.env = instance.env
            obj.updownline = instance.updownline
            obj.serial = instance.serial
            obj.gateway = instance.gateway
            obj.layout = instance.layout
            obj.servers = json.dumps(args.S)
            obj.version = instance.version
            obj.task_type = 'auto'
            obj.created_by = 'admin'
            obj.save()
            kwargs = obj.to_dict()
            kwargs['instance'] = obj
            kwargs['module'] = Modules.objects.get(name=obj.modules, project=obj.project)
            ret, status = AutoDeploy(**kwargs).deploy_run()
            if status == 'success':
                print('自动化发布成功')
            else:
                print('自动化发布失败')
        else:
            print('没有可发布的工单')
    else:
        parser.print_help()
