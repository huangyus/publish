import re

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.response import Response

from api import filters
from commands.apigateway import Nginx
from utils.common import read_log
from .serializers import *
from .tasks import deploy_run
from .models import *


class APIGateWayViewSet(viewsets.ModelViewSet):
    queryset = APIGateWay.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = APIGateWaySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = APIGateWay.objects.all()
        idc_id = self.request.query_params.get('idc_id', None)
        if idc_id is not None:
            idc_id = json.loads(idc_id)
            queryset = queryset.filter(idc__name__in=idc_id)
        return queryset


class GlobalConfigViewSet(viewsets.ModelViewSet):
    queryset = GlobalConfig.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = GlobalConfigSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = GlobalConfig.objects.all()
        apigateway_id = self.request.query_params.get('apigateway_id', None)
        if apigateway_id is not None:
            queryset = queryset.filter(apigateway_id=apigateway_id)
        return queryset


class MapsViewSet(viewsets.ModelViewSet):
    queryset = Maps.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = MapsSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Maps.objects.all()
        apigateway_id = self.request.query_params.get('apigateway_id', None)
        if apigateway_id is not None:
            queryset = queryset.filter(apigateway_id=apigateway_id)
        return queryset


class UpstreamsViewSet(viewsets.ModelViewSet):
    queryset = Upstreams.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = UpsteamsSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Upstreams.objects.all()
        apigateway_id = self.request.query_params.get('apigateway_id', None)
        if apigateway_id is not None:
            queryset = queryset.filter(apigateway_id=apigateway_id)
        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.queryset.filter(id=kwargs['pk'])[0]
        old_name = instance.name
        new_name = request.data['name']
        if old_name != new_name:
            kwargs = instance.to_dict()
            kwargs['deploy_type'] = 'upstreams'
            kwargs['instance'] = instance.apigateway
            kwargs['category_id'] = instance.id
            ngx = Nginx(**kwargs)
            old_filename = '%s.conf' % old_name
            new_filename = '%s.conf' % new_name
            assert not ngx.build_file(filename=new_filename) == False, ('Upstream create %s file error' % new_name)
            assert not ngx.rename(old_filename, new_filename) == False, (
                    'Upstream %s rename to %s file error' % (old_filename, new_filename))
            return super().update(request, *args, **kwargs)
        else:
            return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        kwarg = instance.to_dict()
        kwarg['deploy_type'] = 'upstreams'
        kwarg['instance'] = instance.apigateway
        kwarg['category_id'] = instance.id
        ngx = Nginx(**kwarg)
        if ngx.check_upstream_depend():
            return super().destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': '%s Upstream not delete, vhosts include upstream' % instance.name})


class VhostsViewSet(viewsets.ModelViewSet):
    queryset = Vhosts.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = VhostsSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    filter_backends = (filters.RoleFilterBackend,)

    def get_queryset(self):
        queryset = Vhosts.objects.all()
        apigateway_id = self.request.query_params.get('apigateway_id', None)
        if apigateway_id is not None:
            queryset = queryset.filter(apigateway_id=apigateway_id)
        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.queryset.filter(id=kwargs['pk'])[0]
        old_name = re.split("[ |,]", instance.domain)[0]
        new_name = re.split("[ |,]", request.data['domain'])[0]
        if old_name != new_name:
            kwargs = instance.to_dict()
            kwargs['deploy_type'] = 'vhosts.d'
            kwargs['instance'] = instance.apigateway
            kwargs['category_id'] = instance.id
            ngx = Nginx(**kwargs)
            old_filename = '%s.conf' % old_name
            new_filename = '%s.conf' % new_name
            assert not ngx.build_file(filename=new_filename) == False, ('Vhost create %s file error' % new_name)
            if ngx.rename(old_filename, new_filename):
                return super().update(request, *args, **kwargs)
            else:
                assert not ngx.undo_rename(old_filename, new_filename) == False, ('Vhost rename undo error')
        else:
            return super().update(request, *args, **kwargs)


class DeployVeiwSet(viewsets.ViewSet):
    def list(self, request):
        task_id = self.request.query_params.get('task_id', None)
        deploy_type = self.request.query_params.get('deploy_type', None)
        if task_id is None or deploy_type is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})
        outfile = settings.SALT_LOG + '/' + deploy_type + '/%s.log' % task_id
        data = read_log(outfile)
        return Response({'log': []})

    def post(self, request):
        task_id = self.request.data.get('task_id', None)
        deploy_type = self.request.data.get('deploy_type', None)
        category_id = self.request.data.get('category_id', None)
        if task_id is None or deploy_type is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})
        result = deploy_run(task_id, deploy_type, category_id)
        if not result:
            out_file = settings.SALT_LOG + '/nginx/%s.log' % task_id
            data = read_log(out_file)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)
        return Response(status=status.HTTP_200_OK, data={})
