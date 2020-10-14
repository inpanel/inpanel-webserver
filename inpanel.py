#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019, doudoudzj
# All rights reserved.
#
# InPanel is distributed under the terms of the New BSD License.
# The full license can be found in 'LICENSE'.
'''InPanel Web Server Module.'''

from os import getpid
from os.path import join, dirname

import core.fun as fun
from webserver.bottle import (Bottle, redirect, request, response, run,
                              template)
from common import server_name

root_path = dirname(__file__)
app = Bottle()
pid = str(getpid())
pidfile = '/var/run/inpanel.pid'
certfile = join(root_path, 'certificate', 'inpanel.crt')
keyfile = join(root_path, 'certificate', 'inpanel.key')

# settings of application
settings = {
    'root_path': root_path,
    'data_path': join(root_path, 'data'),
    'conf_path': join(root_path, 'data', 'config.ini'),
    'index_path': join(root_path, 'static', 'index.html'),
    'static_path': join(root_path, 'static'),
    'plugins_path': join(root_path, 'plugins'),
    'xsrf_cookies': True,
    'cookie_secret': ''
}

app_config = {
    'app': app,
    'host': '0.0.0.0',
    'port': 38080,
    'debug': True,
    # 'certfile': certfile,
    'keyfile': keyfile,
    'gzip': True,
    'reloader': True
}


@app.hook('after_request')
def hook_after_request():
    # response.set_header('Server', server_name)
    response.headers['Server'] = server_name
    response.headers['Access-Control-Allow-Origin'] = '*'
    # request.environ['PATH_INFO'] = request.environ['PATH_INFO'].rstrip('/')
    # if request.get_header('Origin'):
    #     response.headers('Access-Control-Allow-Origin', request.get_header('Origin'))
    #     response.headers('Access-Control-Allow-Headers', 'X-ACCESS-TOKEN, Content-Type')
    #     response.headers('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

@app.route('/index', method=['GET'])
def index():
    # response.set_header('Server', server_name)
    return template('<b>Welcome to {{server_name}}</b>!',
                    server_name=server_name)


def init_pid():
    with open(pidfile, 'w') as f:
        f.write(pid)


def init_router(app):
    # app.route('/', ['GET'], fun.server_static)
    app.route('/', ['GET'], fun.index)
    app.route('/client/<server>/', ['GET'], fun.client_server)
    app.route('/static/<filepath:path>', ['GET'], fun.server_static)
    app.route('/xsrf', ['GET'], fun.xsrf)
    app.route('/authstatus', ['GET', 'POST'], fun.authstatus)
    app.route('/login', ['POST'], fun.login)
    app.route(('/hello', '/hello/<name>'), ['GET'], fun.hello)
    app.route('/download/<filename:path>', ['GET'], fun.download)
    app.route('/getclientip', ['GET'], fun.show_client_ip)
    app.error(404, fun.error404)
    # app.error(500, fun.error404)
    app.route(['/version', '/version/', '/version/<type>'], ['GET'], fun.version)


def https_redirect(app):
    # https://github.com/ali01/bottle-sslify/blob/master/bottle_sslify.py
    '''Redirect incoming HTTPS requests to HTTPS'''
    if not request.get_header('X-Forwarded-Proto', 'http') == 'https':
        if request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            code = 301 if app.permanent else 302
            redirect(url, code=code)


if __name__ == '__main__':
    # before_request = app.hook('before_request')
    # before_request(https_redirect(app))
    init_router(app)
    # init_pid()
    run(**app_config)
