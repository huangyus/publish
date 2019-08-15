import json

from rest_framework import serializers
from .models import *

basefield = ('url', 'id', 'created_by', 'created_at', 'updated_at', 'desc')


class APIGateWaySerializer(serializers.HyperlinkedModelSerializer):
    idc = serializers.SlugRelatedField(allow_null=True, slug_field='name', queryset=Datacenter.objects.all())
    layout = serializers.SlugRelatedField(allow_null=True, slug_field='name', queryset=Middlewares.objects.all())
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Projects.objects.all())

    class Meta:
        model = APIGateWay
        fields = basefield + ('name', 'servers', 'idc', 'env', 'cmd', 'home', 'layout', 'custom_command', 'tags')


class GlobalConfigSerializer(serializers.HyperlinkedModelSerializer):
    layout = serializers.SlugRelatedField(allow_null=True, slug_field='name', queryset=Middlewares.objects.all())
    apigateway = serializers.SlugRelatedField(allow_null=True, slug_field='id', queryset=APIGateWay.objects.all())

    class Meta:
        model = GlobalConfig
        fields = basefield + ('apigateway', 'content', 'layout', 'custom_command')


class MapsSerializer(serializers.HyperlinkedModelSerializer):
    layout = serializers.SlugRelatedField(allow_null=True, slug_field='name', queryset=Middlewares.objects.all())
    apigateway = serializers.SlugRelatedField(allow_null=True, slug_field='id', queryset=APIGateWay.objects.all())

    class Meta:
        model = Maps
        fields = basefield + ('apigateway', 'config', 'maps', 'content', 'status', 'layout', 'custom_command')


class UpsteamsSerializer(serializers.HyperlinkedModelSerializer):
    layout = serializers.SlugRelatedField(allow_null=True, slug_field='name', queryset=Middlewares.objects.all())
    apigateway = serializers.SlugRelatedField(allow_null=True, slug_field='id', queryset=APIGateWay.objects.all())

    class Meta:
        model = Upstreams
        fields = basefield + ('name', 'apigateway', 'ip_hash', 'keepalive', 'http_check', 'tcp_check', 'upstreams', 'status', 'layout', 'custom_command', 'content')


class VhostsSerializer(serializers.HyperlinkedModelSerializer):
    layout = serializers.SlugRelatedField(allow_null=True, slug_field='name', queryset=Middlewares.objects.all())
    apigateway = serializers.SlugRelatedField(allow_null=True, slug_field='id', queryset=APIGateWay.objects.all())

    class Meta:
        model = Vhosts
        fields = basefield + ('apigateway', 'domain', 'port', 'rate_limit', 'access_log', 'error_log', 'extras', 'ssl_status', 'ssl_port', 'ssl_port_default', 'http_status', 'ssl_cert_body', 'ssl_key_body', 'ssl_extras', 'dynamics_list', 'statics_list', 'status', 'content', 'layout', 'custom_command')
