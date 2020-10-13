#!/usr/bin/env python
# -*- coding: utf-8 -*-

from webserver.bottle import template, error, static_file, request, response
from common import server_name, app_info, root_path
from os.path import join

def hello(name='World'):
    return template('<b>Hello {{name}}</b>!', name=name)

def xsrf():
    return ''

def authstatus():
    return 'authstatus'

def login():
    response.set_cookie('Set-Cookie', 'authed=eWVz|1601441998|62b24007d60ef3ab112018cc4d91b9569b6d6260; Path=/')
    return {
        'code': 1,
        'msg': "您已登录成功！"
    }

def show_client_ip():
    ip = request.environ.get('REMOTE_ADDR')
    # or ip = request.get('REMOTE_ADDR')
    # or ip = request['REMOTE_ADDR']
    # return template("Your IP is: {{ip}}", ip=ip)
    return ip


def error404(error):
    return '404 NotFound'


def version(type=None):
    if type == 'json':
        return app_info
    return app_info['version']


def download(filename):
    return static_file(filename,
                       root='/path/to/static/files',
                       download=filename,
                       etag=True,
                       headers={'Server': server_name})


def server_static(filepath=None):
    if filepath is None:
        filepath = 'index.html'
    return static_file(filepath,
                       root=join(root_path, 'static'),
                       etag=True,
                       headers={'Server': server_name})

def server_partials(filepath):
    return static_file(filepath,
                       root=join(root_path, 'static', 'partials'),
                       etag=True,
                       headers={'Server': server_name})
