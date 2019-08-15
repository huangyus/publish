import uuid

from django.db import models

from utils.common import encrypt_value


class Notification(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    host = models.CharField(max_length=30, verbose_name="消息服务器", null=True)
    routing_key = models.CharField(max_length=10, verbose_name="队列名称", null=True)
    user = models.CharField(max_length=10, verbose_name="用户名", null=True)
    password = models.CharField(max_length=100, verbose_name="密码", null=True)
    desc = models.TextField(blank=True, null=True, verbose_name="描述")

    def save(self, *args, **kwargs):
        if not self.password.startswith('$encrypted$') and self.password != '':
            self.password = encrypt_value(self.password)
        super(Notification, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '消息通知'
