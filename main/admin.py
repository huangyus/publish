from django.contrib import admin
from .models import *


class MainAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_list',)
    fields = ('name', 'role')
    filter_horizontal = ('role',)

    def role_list(self, obj):
        return ', '.join(['%s' % r.name for r in obj.role.all()])


class ServerAdmin(admin.ModelAdmin):
    list_display = ('ip', 'role_list',)
    fields = ('ip', 'role')
    filter_horizontal = ('role',)

    def role_list(self, obj):
        return ', '.join(['%s' % r.name for r in obj.role.all()])


admin.site.register(Projects, MainAdmin)
admin.site.register(Modules, MainAdmin)
admin.site.register(Datacenter, MainAdmin)
admin.site.register(Servers, ServerAdmin)
admin.site.register(Group, MainAdmin)
admin.site.register(Middlewares, MainAdmin)
admin.site.register(BusinessTemplate, MainAdmin)
admin.site.register(WorkFlowTemplate, MainAdmin)

