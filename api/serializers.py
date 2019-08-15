import json
from django.contrib.auth.models import User
from rest_framework import serializers

from main.models import *
from role.models import Role

basefields = ('url', 'id', 'created_by', 'created_at', 'updated_at', 'desc')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    roles = serializers.SerializerMethodField()
    perms = serializers.SerializerMethodField()
    router = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_roles(self, obj):
        role = Role.objects.filter(users=obj)
        data = []
        for r in role:
            data.append({'id': r.id, 'name': r.name})
        return data

    def get_perms(self, obj):
        role = Role.objects.get(users=obj)
        data = [{'id': p.id, 'codename': p.codename} for p in role.perms.all()]
        return data

    def get_router(self, obj):
        role = Role.objects.get(users=obj)
        data = [r.to_dict() for r in role.routers.all()]
        return data

    def get_name(self, obj):
        return obj.first_name

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'name', 'is_superuser', 'is_staff', 'is_active', 'roles', 'perms', 'router')


class DatacenterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Datacenter
        fields = basefields + ('name', 'location')


class ServersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Servers
        fields = basefields + ('idc', 'hostname', 'ip')


class ProjectsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Projects
        fields = basefields + ('name', 'dv_user', 'sa_user')


class ModulesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Modules
        fields = basefields + ('name', 'project', 'env', 'module_type', 'arch_type', 'cmd_type', 'repo_url', 'repo_type', 'repo_mode', 'repo_user', 'repo_pass', 'repo_result', 'status', 'repo_work', 'repo_ignore', 'dest_user', 'dest_root', 'dest_repo', 'dest_keep')


class MiddlewareSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Middlewares
        fields = basefields + ('name', 'layout_arch', 'version', 'content')


class BusinessSerializer(serializers.HyperlinkedModelSerializer):
    rb_status = serializers.SerializerMethodField()
    rb_version = serializers.SerializerMethodField()
    idc = serializers.SerializerMethodField()

    def get_rb_status(self, obj):
        try:
            instance = Business.objects.filter(modules=obj.modules, project=obj.project, created_at__lte=obj.created_at).order_by('created_at')[1]
            if instance.version:
                return True
        except Exception as e:
            return False

    def get_rb_version(self, obj):
        try:
            instance = Business.objects.filter(modules=obj.modules, project=obj.project, created_at__lte=obj.created_at).order_by('created_at')[1]
            return instance.version
        except Exception as e:
            return ''

    def get_idc(self, obj):
        if obj.idc:
            return json.loads(obj.idc)
        else:
            return []

    class Meta:
        model = Business
        fields = basefields + ('name', 'project', 'idc', 'modules', 'updownline', 'gateway', 'serial', 'confirm', 'env', 'version', 'layout', 'servers', 'task_type', 'status', 'file_mode', 'file_list', 'current', 'cron', 'periodic', 'rb_status', 'rb_version')


class BsTemplateSerializer(serializers.HyperlinkedModelSerializer):
    idc = serializers.SerializerMethodField()

    def get_idc(self, obj):
        if obj.idc:
            return json.loads(obj.idc)
        else:
            return []

    class Meta:
        model = BusinessTemplate
        fields = basefields + ('name', 'project', 'idc', 'modules', 'updownline', 'gateway', 'serial', 'env', 'version', 'layout', 'servers', 'file_mode', 'file_list')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = basefields + ('name', 'project', 'idc', 'servers')


class GroupDepthSerializer(serializers.HyperlinkedModelSerializer):
    servers = serializers.SerializerMethodField()

    def get_servers(self, obj):
        return json.loads(obj.servers)

    class Meta:
        model = Group
        fields = basefields + ('name', 'project', 'idc', 'servers')


class BasicSerializer(serializers.HyperlinkedModelSerializer):
    idc = serializers.SerializerMethodField()

    def get_idc(self, obj):
        if obj.idc:
            return json.loads(obj.idc)
        else:
            return []

    class Meta:
        model = Basic
        fields = basefields + ('name', 'project', 'idc', 'component', 'version', 'layout', 'servers', 'task_type', 'confirm', 'current', 'status')


class BasicTemplateSerializer(serializers.HyperlinkedModelSerializer):
    idc = serializers.SerializerMethodField()

    def get_idc(self, obj):
        if obj.idc:
            return json.loads(obj.idc)
        else:
            return []

    class Meta:
        model = BasicTemplate
        fields = basefields + ('component', 'idc', 'version', 'layout', 'servers')


class LoggerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Logger
        fields = basefields + ('action', 'content', 'value')


class WorkFlowSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkFlow
        fields = basefields + ('name', 'steps', 'confirm', 'task_type', 'status')


class WorkFlowTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkFlowTemplate
        fields = basefields + ('name', 'steps')


class RollBackSerializer(serializers.ModelSerializer):
    business = serializers.SerializerMethodField()

    def get_business(self, obj):
        ret = Business.objects.get(id=obj.business_id)
        return ret.to_dict()

    class Meta:
        model = Rollback
        fields = ('id', 'created_by', 'created_at', 'updated_at', 'desc', 'status', 'version', 'business')
