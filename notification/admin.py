from django.contrib import admin

from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('host', 'routing_key', 'user', 'password')



admin.site.register(Notification, NotificationAdmin)
