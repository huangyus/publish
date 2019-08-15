from django.db import models
from django.db.models import DateTimeField
from django.db.models.fields.related import ManyToManyField
import uuid

from main.models import Datacenter, Projects, Middlewares
from .utils import (build_upstream, build_vhosts)


class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=32, null=True, blank=True)
    desc = models.TextField(blank=True, null=True)

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields + opts.many_to_many:
            if isinstance(f, ManyToManyField):
                if self.pk is None:
                    data[f.name] = []
                else:
                    try:
                        data[f.name] = list(f.value_from_object(self).values_list('pk', flat=True))
                    except Exception as e:
                        data[f.name] = []
            elif isinstance(f, DateTimeField):
                if f.value_from_object(self) is not None:
                    data[f.name] = f.value_from_object(self)
                else:
                    data[f.name] = None
            else:
                data[f.name] = f.value_from_object(self)
        return data

    class Meta:
        abstract = True


class APIGateWay(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    idc = models.ForeignKey(Datacenter, on_delete=models.CASCADE, help_text="数据中心信息", null=True)
    servers = models.CharField(max_length=1024)
    env = models.CharField(max_length=100, help_text="环境名称", blank=True, null=True)
    home = models.CharField(max_length=200, help_text="nginx家目录")
    cmd = models.CharField(max_length=256, help_text="nginx执行命令")
    layout = models.ForeignKey(Middlewares, on_delete=models.CASCADE, null=True)
    custom_command = models.TextField(blank=True)
    tags = models.ManyToManyField(Projects, null=True, blank=True)
    role = models.ManyToManyField('role.Role')

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '负载均衡'


class GlobalConfig(BaseModel):
    apigateway = models.ForeignKey(APIGateWay, on_delete=models.CASCADE, null=True, help_text="负载均衡")
    name = models.CharField(max_length=5, default='nginx.conf', help_text="nginx全局配置文件")
    content = models.TextField(blank=True)
    layout = models.ForeignKey(Middlewares, on_delete=models.CASCADE, null=True)
    custom_command = models.TextField(blank=True)
    role = models.ManyToManyField('role.Role')
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '全局配置'


class Maps(BaseModel):
    apigateway = models.ForeignKey(APIGateWay, on_delete=models.CASCADE, null=True, help_text="负载均衡")
    config = models.TextField(blank=True)
    status = models.BooleanField(default=True)
    maps = models.TextField()
    content = models.TextField(blank=True)
    layout = models.ForeignKey(Middlewares, on_delete=models.CASCADE, null=True)
    custom_command = models.TextField(blank=True)
    role = models.ManyToManyField('role.Role')

    def delete(self, *args, **kwargs):
        from commands.apigateway import Nginx
        kwargs = self.to_dict()
        kwargs['deploy_type'] = 'maps'
        kwargs['instance'] = self.apigateway
        kwargs['category_id'] = self.id
        nginx = Nginx(**kwargs)
        status = nginx.destory()
        if status:
            super(Maps, self).delete()
        assert not False == status, ('%s Map Delete False' % self.desc)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Maps配置'


class Upstreams(BaseModel):
    apigateway = models.ForeignKey(APIGateWay, on_delete=models.CASCADE, null=True, help_text="负载均衡")
    name = models.CharField(max_length=255)
    project = models.CharField(max_length=100, blank=True, null=True)
    module = models.CharField(max_length=100, help_text="模块名称", blank=True, null=True)
    upstreams = models.CharField(max_length=1024)
    ip_hash = models.BooleanField(default=False)
    keepalive = models.CharField(max_length=5, blank=True, null=True)
    http_check = models.BooleanField(default=False)
    tcp_check = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    content = models.TextField(blank=True)
    layout = models.ForeignKey(Middlewares, on_delete=models.CASCADE, null=True)
    custom_command = models.TextField(blank=True)
    role = models.ManyToManyField('role.Role')

    def save(self, *args, **kwargs):
        self.content = build_upstream(self)
        super(Upstreams, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        from commands.apigateway import Nginx
        kwargs = self.to_dict()
        kwargs['deploy_type'] = 'upstreams'
        kwargs['instance'] = self.apigateway
        kwargs['category_id'] = self.id
        nginx = Nginx(**kwargs)
        status = nginx.destory()
        if status:
            super(Upstreams, self).delete()
        else:
            if nginx.redestory():
                print('%s Upstream Delete undo True' % self.name)
            else:
                assert False, ('%s Upstream Delete undo False' % self.name)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('name', 'apigateway')
        verbose_name_plural = 'Upstreams配置'


class Vhosts(BaseModel):
    apigateway = models.ForeignKey(APIGateWay, on_delete=models.CASCADE, null=True, help_text="负载均衡")
    domain = models.CharField(max_length=255, default='')
    port = models.CharField(max_length=10)
    rate_limit = models.TextField(blank=True, null=True)
    access_log = models.CharField(max_length=256, help_text="location访问日志", blank=True)
    error_log = models.CharField(max_length=256, help_text="location错误日志", blank=True)
    extras = models.TextField(help_text="location全局配置扩展参数", blank=True)
    ssl_status = models.BooleanField(default=False)
    ssl_port = models.CharField(max_length=10, blank=True)
    ssl_port_default = models.BooleanField(default=False)
    http_status = models.BooleanField(default=False)
    ssl_cert_body = models.TextField(blank=True)
    ssl_key_body = models.TextField(blank=True)
    ssl_cert_path = models.CharField(max_length=255, blank=True)
    ssl_key_path = models.CharField(max_length=255, blank=True)
    ssl_extras = models.TextField(blank=True)
    dynamics_list = models.TextField(blank=True)
    statics_list = models.TextField(blank=True)
    status = models.BooleanField(default=True)
    content = models.TextField(blank=True)
    layout = models.ForeignKey(Middlewares, on_delete=models.CASCADE, null=True)
    custom_command = models.TextField(blank=True)
    role = models.ManyToManyField('role.Role')

    def save(self, *args, **kwargs):
        self.content = build_vhosts(self)
        super(Vhosts, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        from commands.apigateway import Nginx
        kwargs = self.to_dict()
        kwargs['deploy_type'] = 'vhosts.d'
        kwargs['instance'] = self.apigateway
        kwargs['category_id'] = self.id
        nginx = Nginx(**kwargs)
        status = nginx.destory()
        if status:
            super(Vhosts, self).delete()
        else:
            if nginx.redestory():
                print('%s Vhost Delete undo False' % self.domain)
            else:
                assert False, ('%s Vhost Delete False' % self.domain)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Vhosts配置'
