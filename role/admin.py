from django.contrib import admin
from .models import Router, Role


def choice_name(name):
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
    return name


class RouterAdmin(admin.ModelAdmin):
    list_display = ('name', 'path',)


class RolesAdmin(admin.ModelAdmin):
    list_display = ('name', 'users_list', 'perms_list', 'routers_list')
    list_display_links = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('users', 'perms', 'routers')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'perms':
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                content_type__app_label__in=['main', 'apigateway'])
        elif db_field.name == 'users' or db_field.name == 'routers':
            pass
        else:
            kwargs['required'] = False
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def users_list(self, obj):
        return ', '.join(['%s(%s)' % (u.username, u.first_name) for u in obj.users.all()])

    def perms_list(self, obj):
        return ', '.join(['%s%s' % (choice_name(p.name), p.content_type) for p in obj.perms.all()])

    def routers_list(self, obj):
        return ', '.join([r.name for r in obj.routers.all()])

    users_list.short_description = '用户列表'
    perms_list.short_description = '权限列表'
    routers_list.short_description = '静态路由列表'


class RolesDatacenter(admin.ModelAdmin):
    list_display = ('roles', )


admin.site.register(Router, RouterAdmin)
admin.site.register(Role, RolesAdmin)
