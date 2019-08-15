import copy
import json

from main.models import Logger


class BaseLogginMixin(object):
    allowed_logging_methods = ('post', 'put', 'delete')
    methods_choices = (
        ('post', '创建'),
        ('put', '更新'),
        ('delete', '删除')
    )
    instance = None

    def save(self, *args, **kwargs):
        logger = Logger(**kwargs)
        logger.save()


class DatacenterLoggingMixin(BaseLogginMixin):
    def get_object(self):
        obj = super().get_object()
        self.instance = copy.deepcopy(obj)
        return obj

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if request.method.lower() not in self.allowed_logging_methods:
            return response
        if request.method.lower() == 'delete':
            serializer = super().get_serializer(self.instance, context={'request': request})
            data = serializer.data
        else:
            data = request.data
        log_kwargs = {
            'created_by': data['created_by'],
            'action': request.method,
            'content': dict(self.methods_choices).get(request.method.lower()) + data['name'],
            'value': json.dumps(data),
        }
        self.save(**log_kwargs)
        return response


class ServerLoggingMixin(BaseLogginMixin):
    def get_object(self):
        obj = super().get_object()
        self.instance = copy.deepcopy(obj)
        return obj

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if request.method.lower() not in self.allowed_logging_methods:
            return response
        if request.method.lower() == 'delete':
            serializer = super().get_serializer(self.instance, context={'request': request})
            data = serializer.data
        else:
            data = request.data
        created_by = None
        ip = []
        if isinstance(request.data, list):
            for item in request.data:
                created_by = item['created_by']
                ip.append(item['ip'])
            log_kwargs = {
                'created_by': created_by,
                'action': request.method,
                'content': dict(self.methods_choices).get(request.method.lower()) + '服务器： ' + ', '.join(ip),
                'value': json.dumps(data),
            }
        else:
            log_kwargs = {
                'created_by': data['created_by'],
                'action': request.method,
                'content': dict(self.methods_choices).get(request.method.lower()) + '服务器： ' + data['ip'],
                'value': json.dumps(data),
            }
        self.save(**log_kwargs)
        return response


class ProjectLoggingMixin(BaseLogginMixin):
    def get_object(self):
        obj = super().get_object()
        self.instance = copy.deepcopy(obj)
        return obj

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if request.method.lower() not in self.allowed_logging_methods:
            return response
        if request.method.lower() == 'delete':
            serializer = super().get_serializer(self.instance, context={'request': request})
            data = serializer.data
        else:
            data = request.data
        log_kwargs = {
            'created_by': data['created_by'],
            'action': request.method,
            'content': dict(self.methods_choices).get(request.method.lower()) + '项目： ' + data['name'],
            'value': json.dumps(data),
        }
        self.save(**log_kwargs)
        return response


class ModuleLoggingMixin(BaseLogginMixin):
    def get_object(self):
        obj = super().get_object()
        self.instance = copy.deepcopy(obj)
        return obj

    # def finalize_response(self, request, response, *args, **kwargs):
    #     response = super().finalize_response(request, response, *args, **kwargs)
    #     if request.method.lower() not in self.allowed_logging_methods:
    #         return response
    #     if request.method.lower() == 'delete':
    #         serializer = super().get_serializer(self.instance, context={'request': request})
    #         data = serializer.data
    #     else:
    #         data = request.data
    #     log_kwargs = {
    #         'created_by': data['created_by'],
    #         'action': request.method,
    #         'content': dict(self.methods_choices).get(request.method.lower()) + '模块： ' + data['name'],
    #         'value': json.dumps(data),
    #     }
    #     self.save(**log_kwargs)
    #     return response


class MiddlewareLoggingMixin(BaseLogginMixin):
    def get_object(self):
        obj = super().get_object()
        self.instance = copy.deepcopy(obj)
        return obj

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if request.method.lower() not in self.allowed_logging_methods:
            return response
        if request.method.lower() == 'delete':
            serializer = super().get_serializer(self.instance, context={'request': request})
            data = serializer.data
        else:
            data = request.data
        log_kwargs = {
            'created_by': data['created_by'],
            'action': request.method,
            'content': dict(self.methods_choices).get(request.method.lower()) + '部署编排： ' + data['name'],
            'value': json.dumps(data),
        }
        self.save(**log_kwargs)
        return response


class BusinessLoggingMixin(BaseLogginMixin):
    def get_object(self):
        obj = super().get_object()
        self.instance = copy.deepcopy(obj)
        return obj

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if request.method.lower() not in self.allowed_logging_methods:
            return response
        if request.method.lower() == 'delete':
            serializer = super().get_serializer(self.instance, context={'request': request})
            data = serializer.data
        else:
            data = request.data
        log_kwargs = {
            'created_by': data.get('created_by', None),
            'action': request.method,
            'content': dict(self.methods_choices).get(request.method.lower()) + '业务部署上线单： ' + data['name'],
            'value': json.dumps(data),
        }
        self.save(**log_kwargs)
        return response


class GroupLoggingMixin(BaseLogginMixin):
    def get_object(self):
        obj = super().get_object()
        self.instance = copy.deepcopy(obj)
        return obj

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if request.method.lower() not in self.allowed_logging_methods:
            return response
        if request.method.lower() == 'delete':
            serializer = super().get_serializer(self.instance, context={'request': request})
            data = serializer.data
        else:
            data = request.data
        log_kwargs = {
            'created_by': data['created_by'],
            'action': request.method,
            'content': dict(self.methods_choices).get(request.method.lower()) + '分组： ' + data['name'],
            'value': json.dumps(data),
        }
        self.save(**log_kwargs)
        return response


class BasicLoggingMixin(BaseLogginMixin):
    def get_object(self):
        obj = super().get_object()
        self.instance = copy.deepcopy(obj)
        return obj

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if request.method.lower() not in self.allowed_logging_methods:
            return response
        if request.method.lower() == 'delete':
            serializer = super().get_serializer(self.instance, context={'request': request})
            data = serializer.data
        else:
            data = request.data
        log_kwargs = {
            'created_by': data['created_by'],
            'action': request.method,
            'content': dict(self.methods_choices).get(request.method.lower()) + '基础部署上线单： ' + data['name'],
            'value': json.dumps(data),
        }
        self.save(**log_kwargs)
        return response
