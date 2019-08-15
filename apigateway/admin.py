from django.contrib import admin
from .models import *


class ApiGateWayAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_list',)
    fields = ('name', 'role')
    filter_horizontal = ('role',)

    def role_list(self, obj):
        return ', '.join(['%s' % r.name for r in obj.role.all()])


class GlobalConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_list',)
    fields = ('name', 'role')
    filter_horizontal = ('role',)

    def role_list(self, obj):
        return ', '.join(['%s' % r.name for r in obj.role.all()])


class MapsAdmin(admin.ModelAdmin):
    list_display = ('desc', 'role_list',)
    fields = ('desc', 'role')
    filter_horizontal = ('role',)

    def role_list(self, obj):
        return ', '.join(['%s' % r.name for r in obj.role.all()])


class UpstreamsAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_list',)
    fields = ('name', 'role')
    filter_horizontal = ('role',)

    def role_list(self, obj):
        return ', '.join(['%s' % r.name for r in obj.role.all()])


class VhostsAdmin(admin.ModelAdmin):
    list_display = ('domain', 'role_list',)
    fields = ('domain', 'role')
    filter_horizontal = ('role',)

    def role_list(self, obj):
        return ', '.join(['%s' % r.name for r in obj.role.all()])


admin.site.register(APIGateWay, ApiGateWayAdmin)
admin.site.register(GlobalConfig, GlobalConfigAdmin)
admin.site.register(Upstreams, UpstreamsAdmin)
admin.site.register(Maps, MapsAdmin)
admin.site.register(Vhosts, VhostsAdmin)

