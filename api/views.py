from datetime import datetime

import pytz
from celery import chain
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.decorators import action
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from api.consumers import emit_notification
from commands.autodeploy import AutoDeploy
from commands.command import Version
from utils.common import read_log
from .serializers import *
from .logger import *
from main.models import *
from .tasks import deploy_run, PullRepo, workflow_deploy
from utils import git, svn
from . import filters
from .utils import custom_sql, custom_day, between_days, generate_series
from commands.business import BusinessRollback



def home(request):
    if request.user.is_authenticated:
        return redirect('/api/')
    else:
        return redirect('/accounts/login/')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = User.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(username=username)
        return queryset


class DatacenterViewSet(DatacenterLoggingMixin, viewsets.ModelViewSet):
    queryset = Datacenter.objects.all()
    serializer_class = DatacenterSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Datacenter.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset


class ServersViewSet(ServerLoggingMixin, viewsets.ModelViewSet):
    queryset = Servers.objects.all()
    serializer_class = ServersSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Servers.objects.all()
        idc_id = self.request.query_params.get('idc_id', None)
        hostname = self.request.query_params.get('hostname', None)
        if idc_id is not None:
            queryset = queryset.filter(idc=idc_id)
            if hostname is not None:
                queryset = queryset.filter(hostname=hostname)
        return queryset

    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        if many:
            serializer = self.get_serializer(data=request.data, many=many)
        else:
            serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectsViewSet(ProjectLoggingMixin, viewsets.ModelViewSet):
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Projects.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset


class ModulesViewSet(ModuleLoggingMixin, viewsets.ModelViewSet):
    queryset = Modules.objects.all()
    serializer_class = ModulesSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Modules.objects.all()
        project = self.request.query_params.get('project', None)
        name = self.request.query_params.get('name', None)
        if project is not None:
            queryset = queryset.filter(project=project)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset

    @action(methods=['post'], detail=False, url_path='refresh')
    def refresh(self, request):
        module_id = self.request.data.get('module_id', None)
        if module_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})
        PullRepo(module_id, refresh=True)
        return Response(status=status.HTTP_200_OK, data={})


class MiddlewareViewSet(MiddlewareLoggingMixin, viewsets.ModelViewSet):
    queryset = Middlewares.objects.all()
    serializer_class = MiddlewareSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Middlewares.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset


class BusinessViewSet(BusinessLoggingMixin, viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Business.objects.all()
        business_id = self.request.query_params.get('task_id', None)
        business_modules = self.request.query_params.get('module', None)
        name = self.request.query_params.get('name', None)
        if business_id is not None:
            queryset = queryset.filter(id=business_id)
        if business_modules is not None:
            queryset = queryset.filter(modules=business_modules)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cron = request.data.get('cron', None)
        periodic = request.data.get('periodic', None)
        if cron and periodic:
            period = datetime.strptime(periodic, '%Y-%m-%d %H:%M:%S')
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=period.minute,
                hour=period.hour,
                day_of_week=period.day,
                day_of_month=period.month,
                month_of_year=period.year,
                timezone=pytz.timezone('Asia/Shanghai')
            )
            PeriodicTask.objects.create(
                crontab=schedule,
                name='Timed Task',
                task='api.task.deploy_run'
            )
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cron and instance.periodic:
            period = datetime.strptime(instance.periodic, '%Y-%m-%d %H:%M:%S')
            schedule = CrontabSchedule.objects.get(
                minute=period.minute,
                hour=period.hour,
                day_of_week=period.day,
                day_of_month=period.month,
                month_of_year=period.year,
                timezone=pytz.timezone('Asia/Shanghai')
            )
            periodic = PeriodicTask.objects.get(
                crontab=schedule,
                name='Timed Task',
                task='api.task.deploy_run'
            )
            periodic.delete()
            schedule.delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BsTemplateViewSet(viewsets.ModelViewSet):
    queryset = BusinessTemplate.objects.all()
    serializer_class = BsTemplateSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = BusinessTemplate.objects.all()
        template_id = self.request.query_params.get('template_id', None)
        project = self.request.query_params.get('project', None)
        name = self.request.query_params.get('name', None)
        if template_id is not None:
            queryset = queryset.filter(id=template_id)
        if project is not None:
            queryset = queryset.filter(project=project)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset


class GroupViewSet(GroupLoggingMixin, viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Group.objects.all()
        project = self.request.query_params.get('project', None)
        modules = self.request.query_params.get('modules', None)
        idc = self.request.query_params.get('idc', None)
        if project and modules and idc:
            queryset = queryset.filter(project=project, name=project + '_' + modules, idc__in=json.loads(idc))
        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        if 'list' == self.action:
            serializer_class = GroupDepthSerializer
        else:
            serializer_class = GroupSerializer
        return serializer_class(*args, **kwargs)


class BasicViewSet(BasicLoggingMixin, viewsets.ModelViewSet):
    queryset = Basic.objects.all()
    serializer_class = BasicSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Basic.objects.all()
        basic_id = self.request.query_params.get('task_id', None)
        name = self.request.query_params.get('name', None)
        if basic_id is not None:
            queryset = queryset.filter(id=basic_id)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset


class BasicTemplateViewSet(viewsets.ModelViewSet):
    queryset = BasicTemplate.objects.all()
    serializer_class = BasicTemplateSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = BasicTemplate.objects.all()
        template_id = self.request.query_params.get('template_id', None)
        name = self.request.query_params.get('name', None)
        if template_id is not None:
            queryset = queryset.filter(id=template_id)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset


class WorkFlowViewSet(viewsets.ModelViewSet):
    queryset = WorkFlow.objects.all()
    serializer_class = WorkFlowSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)


class WorkFlowTemplateViewSet(viewsets.ModelViewSet):
    queryset = WorkFlowTemplate.objects.all()
    serializer_class = WorkFlowTemplateSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = WorkFlowTemplate.objects.all()
        template_id = self.request.query_params.get('template_id', None)
        name = self.request.query_params.get('name', None)
        if template_id is not None:
            queryset = queryset.filter(id=template_id)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset


class LoggerViewSet(viewsets.ModelViewSet):
    queryset = Logger.objects.all()
    serializer_class = LoggerSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)


class VersionViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    def list(self, request):
        data = []
        project = self.request.query_params.get('p', None)
        module = self.request.query_params.get('m', None)
        if module is not None:
            m = Modules.objects.get(name=module, project=project)
            if m.repo_type == 'git':
                if m.repo_mode == '1':
                    data = git.getBranchList(m)
                if m.repo_mode == '2':
                    data = git.gitTagList(m)
            if m.repo_type == 'svn':
                if m.repo_mode == '1':
                    data = svn.getBranchList(m)
                if m.repo_mode == '2':
                    data = svn.getCommitList(m)
                if m.repo_mode == '3':
                    data = svn.getCommitList(m)
        return Response(data)


class DeployViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    def list(self, request):
        task_id = self.request.query_params.get('task_id', None)
        deploy_type = self.request.query_params.get('deploy_type', None)
        if task_id is None or deploy_type is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})
        if deploy_type == 'workflow':
            instance = WorkFlow.objects.get(id=task_id)
            data = json.loads(TaskLog.objects.get(id=instance.log_id).log_text)
        else:
            instance = Business.objects.get(id=task_id)
            data = json.loads(TaskLog.objects.get(id=instance.log_id).log_text)
            if not data:
                outfile = settings.SALT_LOG + '/' + deploy_type + '/%s.log' % task_id
                data = read_log(outfile)
        return Response({'log': data})

    def post(self, request):
        task_id = self.request.query_params.get('task_id', None)
        deploy_type = self.request.query_params.get('deploy_type', None)
        if task_id is None or deploy_type is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})
        if deploy_type == 'workflow':
            wf = WorkFlow.objects.get(id=task_id)
            steps = json.loads(wf.steps)
            chains = []
            for idx, step in enumerate(steps):
                step['created_at'] = Version(wf.created_at)
                step['id'] = task_id
                if idx == 0:
                    # workflow_deploy(running=True, **step)
                    chains.append(workflow_deploy.s(running=True, **step))
                else:
                    # workflow_deploy(running=True, **step)
                    chains.append(workflow_deploy.s(**step))
            ret = chain(chains)()
            if ret.get():
                emit_notification(task_id, {'message': 'end'})
        else:
            deploy_run(task_id, deploy_type)
        return Response(status=status.HTTP_200_OK, data={})


class RollbackViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Rollback.objects.all()
        task_id = self.request.query_params.get('task_id', None)
        instance = Business.objects.get(id=task_id)
        business = Business.objects.filter(modules=instance.modules, created_at__lt=instance.created_at)[0]
        if task_id is not None:
            queryset = business.rollback_set.all()
        serializer = RollBackSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        task_id = self.request.query_params.get('task_id', None)
        deploy_type = self.request.query_params.get('deploy_type', None)
        business = Business.objects.get(id=task_id)
        if business.status != 'success':
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': '此工单不允许回滚'})
        if task_id is None or deploy_type is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})
        kwargs = business.to_dict()
        kwargs['instance'] = business
        kwargs['module'] = Modules.objects.get(name=business.modules)
        rollback = BusinessRollback(**kwargs)
        recode, message = rollback.run()
        if not recode:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': message})
        return Response(status=status.HTTP_200_OK, data={'message': message})


class DashBoardViewSet(viewsets.ViewSet):
    def list(self, request):
        start, end = custom_day()
        business = custom_sql("select COUNT(*) as sum, DATE_FORMAT(created_at, %s) as day from main_business WHERE created_at BETWEEN %s and %s GROUP BY day", ["%Y-%m-%d", start, end])
        basic = custom_sql("select COUNT(*) as sum, DATE_FORMAT(created_at, %s) as day from main_basic WHERE created_at BETWEEN %s and %s GROUP BY day", ["%Y-%m-%d", start, end])
        zone = between_days(start, end)
        bseries = generate_series(business, zone)
        cseries = generate_series(basic, zone)
        return Response(status=status.HTTP_200_OK, data={'business': bseries, 'basic': cseries})


class DashBoardPieViewSet(viewsets.ViewSet):
    def list(self, request):
        start, end = custom_day()
        business = custom_sql("select count(*) as sum, modules from main_business WHERE created_at BETWEEN %s and %s GROUP BY modules ORDER BY sum desc LIMIT 10", [start, end])
        names = []
        bseriers = []
        for b in business:
            names.append(b[1])
            bseriers.append({'value': b[0], 'name': b[1]})
        return Response(status=status.HTTP_200_OK, data={'names': names, 'data': bseriers})


class AutoDeployViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response(status=status.HTTP_200_OK, data=[])

    def post(self, request):
        project = self.request.data.get('project', None)
        module = self.request.data.get('module', None)
        servers = self.request.data.get('servers', None)
        if project is not None and module is not None and servers is not None:
            instance = Business.objects.get(project=project, modules=module, status='success', current=True)
            if instance:
                obj = Business()
                obj.name = '%s-%s-%s' % (datetime.now().strftime('%Y%m%d%H%M%S'), project, module)
                obj.project = project
                obj.modules = module
                obj.env = instance.env
                obj.updownline = instance.updownline
                obj.serial = instance.serial
                obj.gateway = instance.gateway
                obj.layout = instance.layout
                obj.servers = json.dumps(servers)
                obj.version = instance.version
                obj.task_type = 'auto'
                obj.created_by = 'admin'
                obj.save()
                kwargs = obj.to_dict()
                kwargs['instance'] = obj
                kwargs['module'] = Modules.objects.get(name=obj.modules, project=obj.project)
                ret, state = AutoDeploy(**kwargs).deploy_run()
                if state == 'success':
                    return Response(status=status.HTTP_200_OK, data={'msg': '自动扩容成功'})
                else:
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'msg': '自动扩容失败'})

            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'msg': '当前没有可用的部署工单'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'msg': '请求参数有问题'})
