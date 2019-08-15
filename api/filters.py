import copy

from rest_framework import filters

from role.models import Role


class RoleFilterBackend(filters.BaseFilterBackend):
    """通过role筛选数据"""

    @staticmethod
    def _get_role(request):
        try:
            role = Role.objects.get(users=request.user)
        except Exception as e:
            print(e)
            return None
        return role

    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        if view.basename == 'user':
            if request.user.is_superuser:
                return queryset
            else:
                return queryset.filter(username=request.user.username)
        role = self._get_role(request)
        new_queryset = copy.deepcopy(queryset)
        try:
            obj = getattr(role, view.basename + '_set')
            filters_data = [str(i.id) for i in getattr(obj, 'all')()]
            queryset = queryset.filter(id__in=filters_data)
        except AttributeError as e:
            queryset = queryset.none()

        queryset = queryset | new_queryset.filter(created_by=request.user.username)
        return queryset
