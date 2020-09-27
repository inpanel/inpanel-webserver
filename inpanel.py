#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bottle import Bottle, route, run, template, error, static_file, request, response
from os.path import join
import fun
from common import root_path, server_name

app = Bottle()

# settings of application
settings = {
    'root_path': root_path,
    'data_path': join(root_path, 'data'),
    'conf_path': join(root_path, 'data', 'config.ini'),
    'index_path': join(root_path, 'static', 'index.html'),
    'static_path': join(root_path, 'static'),
    'plugins_path': join(root_path, 'plugins'),
    'xsrf_cookies': True,
    'cookie_secret': '',
    'gzip': True
}

@app.route('/index', method=['GET'])
def index():
    response.set_header('Server', server_name)
    return template('<b>Welcome to {{server_name}}</b>!', server_name=server_name)

app.route('/', ['GET'], fun.server_static)
app.route('/xsrf', ['GET'], fun.xsrf)
app.route('/hello/<name>', ['GET'], fun.hello)
app.route('/static/', ['GET'], fun.server_static)
app.route('/static/<filepath:path>', ['GET'], fun.server_static)
app.route('/partials/<filepath:path>', ['GET'], fun.server_partials)
app.route('/download/<filename:path>', ['GET'], fun.download)
app.route('/getclientip', ['GET'], fun.show_client_ip)
app.error(404, fun.error404)
app.route('/version', ['GET'], fun.version)
app.route('/version/<type>', ['GET'], fun.version)

if __name__ == '__main__':
    run(app=app, host='localhost', port=38080, debug=True)
