from bottle import template, error, static_file, request, response
from common import server_name, app_info, root_path
from os.path import join

def hello(name):
    response.set_header('Server', server_name)
    return template('<b>Hello {{name}}</b>!', name=name)


def xsrf():
    response.set_header('Server', server_name)
    return ''


def authstatus():
    response.set_header('Server', server_name)
    return 'authstatus'

def login():
    response.set_header('Server', server_name)
    return {
        'token': 343434
    }

def show_client_ip():
    response.set_header('Server', server_name)
    ip = request.environ.get('REMOTE_ADDR')
    # or ip = request.get('REMOTE_ADDR')
    # or ip = request['REMOTE_ADDR']
    return template("Your IP is: {{ip}}", ip=ip)


def error404(error):
    response.set_header('Server', server_name)
    return '404 NotFound'


def version(type=None):
    response.set_header('Server', server_name)
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
