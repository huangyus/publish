from django.db import models
import uuid

from django.db.models import ManyToManyField, DateTimeField

from utils.common import encrypt_value


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
                    except AttributeError:
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


class Projects(BaseModel):
    """项目管理"""
    name = models.CharField(max_length=100, help_text="项目名称", unique=True)
    dv_user = models.CharField(max_length=1024, help_text="开发人员", blank=True, null=True)
    sa_user = models.CharField(max_length=1024, help_text="运维人员", blank=True, null=True)
    role = models.ManyToManyField('role.Role')

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '项目管理'


class Modules(BaseModel):
    """业务代码模块"""
    name = models.CharField(max_length=100, help_text="模块名称")
    project = models.CharField(max_length=100, help_text="项目名称")
    env = models.CharField(max_length=100, help_text="环境名称")
    module_type = models.IntegerField(help_text="模块类型")
    cmd_type = models.BooleanField(default=False, help_text="命令是否生成文件")
    arch_type = models.CharField(max_length=20, help_text="架构类型", blank=True, null=True)
    repo_url = models.CharField(max_length=100, help_text="仓库地址", blank=True, null=True)
    repo_user = models.CharField(max_length=100, help_text="仓库用户名", blank=True, null=True)
    repo_pass = models.CharField(max_length=100, help_text="仓库密码", blank=True, null=True)
    repo_work = models.CharField(max_length=200, help_text="代码检出仓库", blank=True, null=True)
    repo_type = models.CharField(max_length=50, help_text="代码仓库类型", blank=True, null=True)
    repo_mode = models.CharField(max_length=50, help_text='仓库分支类型', blank=True, null=True)
    repo_ignore = models.TextField(help_text="排除文件", blank=True, null=True)
    repo_result = models.TextField(blank=True, null=True, default='')
    dest_user = models.CharField(max_length=50, help_text="目标机器用户", blank=True, null=True)
    dest_root = models.CharField(max_length=200, help_text="目标机器代码部署路径", blank=True, null=True)
    dest_repo = models.CharField(max_length=200, help_text="目标机器代码存储路径", blank=True, null=True)
    dest_keep = models.CharField(max_length=30, help_text="目标机器代码历史保留版本", blank=True, null=True)
    version = models.CharField(max_length=100, help_text="代码版本", blank=True, null=True)
    status = models.BooleanField(default=False)
    role = models.ManyToManyField('role.Role')

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    def save(self, *args, **kwargs):
        if not self.repo_pass.startswith('$encrypted$') and self.repo_pass != '':
            self.repo_pass = encrypt_value(self.repo_pass)
        super(Modules, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '模块管理'
        unique_together = ('name', 'project',)


class Middlewares(BaseModel):
    """saltstack | ansible 编排代码"""
    name = models.CharField(max_length=100, help_text="编排名称", unique=True)
    layout_arch = models.CharField(max_length=20, help_text="编排架构语言")
    version = models.CharField(max_length=50, help_text="编排名称")
    content = models.TextField(default='')
    role = models.ManyToManyField('role.Role')

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '部署编排'


class Business(BaseModel):
    """业务代码部署"""
    name = models.CharField(max_length=100, help_text="业务部署上线单名称", unique=True)
    project = models.CharField(max_length=100, help_text="项目名称", blank=True)
    idc = models.CharField(max_length=100, help_text="数据中心", blank=True)
    modules = models.CharField(max_length=100, help_text="模块名称", blank=True)
    updownline = models.BooleanField(default=False, help_text="上下线开关")
    gateway = models.CharField(max_length=255, help_text="网关信息", null=True)
    serial = models.BooleanField(default=False, help_text="串行/并行开关")
    confirm = models.BooleanField(default=False, help_text="二次确认")
    env = models.CharField(max_length=100, help_text="环境名称", blank=True, null=True)
    version = models.CharField(max_length=100, help_text="业务代码版本", blank=True)
    servers = models.CharField(max_length=1024, default='', help_text='服务器列表')
    layout = models.CharField(max_length=100, help_text="编排名称", blank=True)
    file_mode = models.CharField(max_length=5, default='1', help_text="业务部署增量或者全量", blank=True, null=True)
    success_server = models.CharField(max_length=1024, default='', help_text='服务器成功列表')
    failed_server = models.CharField(max_length=1024, default='', help_text='服务器失败列表')
    file_list = models.TextField(help_text="增量文件列表", blank=True, null=True)
    status = models.CharField(max_length=50, default='pending', help_text='发布状态')
    task_type = models.CharField(max_length=10, default='simple', help_text="工单类型")
    current = models.BooleanField(default=False, help_text="当前最新版本")
    cron = models.BooleanField(default=False, help_text='是否开启定时任务')
    periodic = models.CharField(max_length=50, help_text='定时任务时间', null=True, blank=True)
    log_id = models.CharField(max_length=36, default='')
    role = models.ManyToManyField('role.Role')

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    class Meta:
        ordering = ['-created_at']
        permissions = (
            ('run_deploy', '运行'),
        )
        verbose_name = '单业务部署'


class Rollback(BaseModel):
    status = models.CharField(max_length=50, help_text='回滚状态', blank=True, null=True)
    version = models.CharField(max_length=20, help_text="业务代码版本", blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)


class WorkFlow(BaseModel):
    """工作流部署"""
    name = models.CharField(max_length=100, help_text="工作流部署上线单名称", unique=True)
    steps = models.TextField(null=True)
    confirm = models.BooleanField(default=False, help_text="二次确认")
    task_type = models.CharField(max_length=10, default='workflow', help_text="工单类型")
    status = models.CharField(max_length=5, default='pending', help_text='发布状态')
    log_id = models.CharField(max_length=36, default='')
    role = models.ManyToManyField('role.Role')

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    class Meta:
        ordering = ['-created_at']
        permissions = (
            ('run_deploy', '运行'),
        )
        verbose_name = '工作流部署'


class BusinessTemplate(BaseModel):
    """业务代码部署模版"""
    name = models.CharField(max_length=100, help_text="业务部署模版名称", unique=True)
    project = models.CharField(max_length=100, help_text="项目名称", blank=True)
    idc = models.CharField(max_length=100, help_text="数据中心", blank=True)
    modules = models.CharField(max_length=100, help_text="模块名称")
    updownline = models.BooleanField(default=False, help_text="上下线开关")
    gateway = models.CharField(max_length=255, help_text="网关信息", null=True)
    serial = models.BooleanField(default=False, help_text="串行/并行开关")
    confirm = models.BooleanField(default=False, help_text="二次确认")
    env = models.CharField(max_length=100, help_text="环境名称", blank=True, null=True)
    version = models.CharField(max_length=100, help_text="业务代码版本")
    servers = models.CharField(max_length=1024, default='', help_text='服务器列表')
    layout = models.CharField(max_length=100, help_text="编排名称")
    file_mode = models.CharField(max_length=5, default='1', help_text="业务部署增量或者全量", blank=True, null=True)
    file_list = models.TextField(help_text="增量文件列表", blank=True, null=True)
    cron = models.BooleanField(default=False, help_text='是否开启定时任务')
    periodic = models.CharField(max_length=50, help_text='定时任务时间', null=True, blank=True)
    role = models.ManyToManyField('role.Role')

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '单部署模版'


class TaskLog(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    log_text = models.TextField()


class Basic(BaseModel):
    """中间件部署"""
    name = models.CharField(max_length=100, help_text="基础组件上线单名称", unique=True)
    project = models.CharField(max_length=100, help_text="项目名称", blank=True)
    idc = models.CharField(max_length=100, help_text="数据中心", blank=True)
    component = models.CharField(max_length=100, help_text="中间件名称")
    version = models.CharField(max_length=100, help_text="中间件版本", blank=True)
    env = models.CharField(max_length=100, help_text="环境名称")
    servers = models.CharField(max_length=1024, default='', help_text='服务器列表')
    layout = models.CharField(max_length=36, help_text="编排名称")
    task_type = models.CharField(max_length=10, default='simple', help_text="工单类型")
    confirm = models.BooleanField(default=False, help_text="二次确认")
    status = models.CharField(max_length=50, default='pending', help_text='发布状态')
    current = models.BooleanField(default=False, help_text="当前最新版本")
    log_id = models.CharField(max_length=36, default='')
    role = models.ManyToManyField('role.Role')

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    class Meta:
        ordering = ['-created_at']
        permissions = (
            ('run_deploy', '运行'),
        )
        verbose_name = '中间件部署'


class BasicTemplate(BaseModel):
    """中间件部署模版"""
    component = models.CharField(max_length=100, help_text="中间件名称")
    version = models.CharField(max_length=100, help_text="中间件版本", blank=True)
    env = models.CharField(max_length=100, help_text="环境名称")
    idc = models.CharField(max_length=100, help_text="数据中心", blank=True)
    servers = models.CharField(max_length=1024, default='', help_text='服务器列表')
    layout = models.CharField(max_length=36, help_text="编排名称")
    confirm = models.BooleanField(default=False, help_text="二次确认")
    task_type = models.CharField(max_length=10, default='simple', help_text="工单类型")

    def __str__(self):
        return '%s - %s' % (self.component, self.created_by)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '中间件模版'


class WorkFlowTemplate(BaseModel):
    """工作流模版"""
    name = models.CharField(max_length=100, help_text="工作流模版名称", unique=True)
    steps = models.TextField()
    role = models.ManyToManyField('role.Role')

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '工作流模版'


class Datacenter(BaseModel):
    """数据中心"""
    name = models.CharField(max_length=100, help_text="机房名称", unique=True)
    location = models.TextField(help_text="机房位置")
    role = models.ManyToManyField('role.Role')
    # project = models.CharField(max_length=100, help_text="项目名称", blank=True)

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '数据中心'


class Group(BaseModel):
    """模块-服务器 分组"""
    name = models.CharField(max_length=100, help_text="分组名称")
    project = models.CharField(max_length=100, help_text="项目名称", blank=True, null=True)
    idc = models.CharField(max_length=100, help_text="数据中心名称", blank=True, null=True)
    servers = models.CharField(max_length=1024, default='', help_text='服务器列表')
    role = models.ManyToManyField('role.Role')

    def __str__(self):
        return '%s - %s' % (self.name, self.created_by)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('name', 'project', 'idc')
        verbose_name_plural = '分组管理'


class Servers(BaseModel):
    idc = models.CharField(max_length=36)
    hostname = models.CharField(max_length=100, help_text="服务器主机名", unique=True)
    ip = models.GenericIPAddressField(unique=True)
    public_ip = models.GenericIPAddressField(blank=True, null=True)
    sn = models.CharField(max_length=128, null=True, blank=True, help_text="服务器sn号")
    cpu_model = models.CharField(max_length=64, null=True, blank=True, help_text="服务器CPU模式")
    cpu_count = models.IntegerField(null=True, help_text="服务器cpu数量")
    cpu_cores = models.IntegerField(null=True, help_text="服务器cpu核数")
    cpu_vcpus = models.IntegerField(null=True, help_text="服务器cpu虚拟核数")
    memory = models.CharField(max_length=64, null=True, blank=True, help_text="内存")
    disk_total = models.CharField(max_length=1024, null=True, blank=True, help_text="磁盘数量")
    models.CharField(max_length=1024, null=True, blank=True, help_text="磁盘信息")
    os = models.CharField(max_length=128, null=True, blank=True, help_text="操作系统")
    os_version = models.CharField(max_length=16, null=True, blank=True, help_text="操作系统版本")
    os_arch = models.CharField(max_length=16, blank=True, null=True, help_text="操作系统架构")
    role = models.ManyToManyField('role.Role')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '服务器管理'


class Logger(BaseModel):
    """日志审计"""
    action = models.CharField(max_length=100, help_text="操作动作")
    content = models.CharField(max_length=100, help_text="操作内容")
    value = models.TextField(help_text="操作实际内容", blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '日志审计'
