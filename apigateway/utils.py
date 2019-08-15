import copy
import json
import os

from jinja2 import Environment, FileSystemLoader
from django.conf import settings


def build_file(path, filename, text):
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.isfile(os.path.join(path, filename)):
        os.mknod(os.path.join(path, filename), mode=0o644)
    else:
        f = open(os.path.join(path, filename), 'r+')
        f.truncate()
        f.close()
    with open(os.path.join(path, filename), 'w') as f:
        text = text.replace('\r\n', '\n')
        f.write(text)
    print("build file: %s , text data: %s" % filename, text)


def build_config(instance, nginx_conf_path):
    new_instance = copy.deepcopy(instance)
    # new_instance.extras = json.loads(new_instance.extras)
    # new_instance.log_format = json.loads(new_instance.log_format)
    data = new_instance.to_dict()
    data['nginx_conf_path'] = nginx_conf_path
    ngx = Nginx(data)
    text = ngx.generate_nginx()
    return text


def build_upstream(instance):
    new_instance = copy.deepcopy(instance)
    new_instance.upstreams = json.loads(new_instance.upstreams)
    ngx = Nginx(new_instance.to_dict())
    text = ngx.generate_upstream()
    return text


def build_maps(instance):
    new_instance = copy.deepcopy(instance)
    new_instance.maps = json.loads(new_instance.maps)
    new_instance.config = json.loads(new_instance.config)
    ngx = Nginx(new_instance.to_dict())
    text = ngx.generate_maps()
    return text


def build_cert(instance):
    from .models import APIGateWay
    apigetway = APIGateWay.objects.get(id=instance.apigateway_id)
    if instance.ssl_status:
        path = os.path.join(settings.NGINX_BASE, apigetway.name, 'certs')
        build_file(path=path, filename='%s.cert' % instance.id, text=instance.ssl_cert_body)
        build_file(path=path, filename='%s.key' % instance.id, text=instance.ssl_key_body)
        instance.ssl_cert_path = '../certs/%s.cert' % instance.id
        instance.ssl_key_path = '../certs/%s.key' % instance.id
    return instance


def build_vhosts(instance):
    instance = build_cert(instance)
    new_instance = copy.deepcopy(instance)
    new_instance.extras = json.loads(instance.extras)
    new_instance.dynamics_list = json.loads(instance.dynamics_list)
    new_instance.statics_list = json.loads(instance.statics_list)
    for dynamics in new_instance.dynamics_list:
        dynamics['location_extra'] = json.loads(dynamics['location_extra'])
        dynamics['location_lua'] = json.loads(dynamics['location_lua'])
    for statics in new_instance.statics_list:
        statics['location_extra'] = json.loads(statics['location_extra'])
    new_instance.ssl_extras = json.loads(new_instance.ssl_extras)
    ngx = Nginx(new_instance.to_dict())
    text = ngx.generate_vhost()
    return text


class Nginx(object):
    def __init__(self, config):
        self.config = config
        self.template_path = os.path.join(settings.BASE_DIR, 'apigateway', 'template')

    def generate_nginx(self):
        template = self._generate_template('nginx.jinja2')
        render = template.render(self.config)
        return render

    def generate_maps(self):
        template = self._generate_template('maps.jinja2')
        render = template.render(self.config)
        return render

    def generate_upstream(self):
        template = self._generate_template('upstream.jinja2')
        render = template.render(self.config)
        return render

    def generate_vhost(self):
        template = self._generate_template('vhost.jinja2')
        render = template.render(self.config)
        return render

    def generate_location(self):
        template = self._generate_template('location.jinja2')
        render = template.render(self.config)
        return render

    def _generate_template(self, template_name):
        j2_env = Environment(loader=FileSystemLoader(os.path.join(self.template_path)))
        return j2_env.get_template(template_name)


def scan_files(directory):
    data = []
    for dirName, subdirList, fileList in os.walk(directory):
        name = os.path.basename(dirName)
        files_list = []
        for fname in fileList:
            files_list.append(fname)
        data.append({name: files_list})
    return data
