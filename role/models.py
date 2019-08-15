from django.db import models
from django.contrib.auth.models import User, Permission
from django.db.models import ManyToManyField, DateTimeField

# from main.models import Projects, Modules, Group, Middlewares, Datacenter, BusinessTemplate, WorkFlowTemplate
# from apigateway.models import APIGateWay, GlobalConfig, Maps, Upstreams, Vhosts


class Router(models.Model):
    name = models.CharField(max_length=100, help_text="静态路由名称")
    path = models.CharField(max_length=255, help_text="静态路由路径")

    def __str__(self):
        return self.name

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields + opts.many_to_many:
            if isinstance(f, ManyToManyField):
                if self.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = list(f.value_from_object(self).values_list('pk', flat=True))
            elif isinstance(f, DateTimeField):
                if f.value_from_object(self) is not None:
                    data[f.name] = f.value_from_object(self)
                else:
                    data[f.name] = None
            else:
                data[f.name] = f.value_from_object(self)
        return data

    class Meta:
        db_table = 'auth_router'
        verbose_name_plural = '静态路由'


class Role(models.Model):
    name = models.CharField(max_length=100, help_text="角色名称", verbose_name='角色名称')
    users = models.ManyToManyField(User, help_text="用户名称", verbose_name='用户')
    perms = models.ManyToManyField(Permission, help_text="用户权限", verbose_name='权限')
    routers = models.ManyToManyField(Router, help_text="静态路由名称", verbose_name='静态路由')
    # projects = models.ManyToManyField(Projects, help_text="项目名称", verbose_name='项目')
    # modules = models.ManyToManyField(Modules, help_text="模块名称", verbose_name='模块')
    # groups = models.ManyToManyField(Group, help_text="分组", verbose_name='分组')
    # middlewares = models.ManyToManyField(Middlewares, help_text="部署编排名称", verbose_name='部署编排')
    # datacenter = models.ManyToManyField(Datacenter, help_text="数据中心", verbose_name='数据中心')
    # bstemplate = models.ManyToManyField(BusinessTemplate, help_text="单部署模版", verbose_name='单部署模版')
    # wftemplate = models.ManyToManyField(WorkFlowTemplate, help_text="工作流模版", verbose_name='工作流模版')
    # apigateway = models.ManyToManyField(APIGateWay, help_text="负载均衡", verbose_name='负载均衡')
    # globalconfig = models.ManyToManyField(GlobalConfig, help_text="Nginx全局配置", verbose_name='Nginx全局配置')
    # maps = models.ManyToManyField(Maps, verbose_name="Nginx Map配置")
    # upstreams = models.ManyToManyField(Upstreams, verbose_name="Nginx Upstream配置")
    # vhosts = models.ManyToManyField(Vhosts, verbose_name="Nginx Vhosts配置")

    def __str__(self):
        return self.name

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields + opts.many_to_many:
            if isinstance(f, ManyToManyField):
                if self.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = list(f.value_from_object(self).values_list('pk', flat=True))
            elif isinstance(f, DateTimeField):
                if f.value_from_object(self) is not None:
                    data[f.name] = f.value_from_object(self)
                else:
                    data[f.name] = None
            else:
                data[f.name] = f.value_from_object(self)
        return data

    class Meta:
        db_table = 'auth_role'
        verbose_name_plural = '角色'


def permissions_new_str(self):
    name = self.name
    if 'Can delete' in name:
        name = '删除'
    if 'Can add' in name:
        name = '添加'
    if 'Can change' in name:
        name = '修改'
    if 'Can view' in name:
        name = '查看'
    if 'Can run' in name:
        name = '运行'

    return "{} | {}".format(
        self.content_type,
        name
    )


def users_new_str(self):
    return "{}({})".format(self.username, self.first_name)


Permission.__str__ = permissions_new_str
User.__str__ = users_new_str
