#!/usr/bin/python
# -*- encoding: utf8 -*-
#
# Copyright (c) 2020, doudoudzj
# All rights reserved.
#
# InPanel is distributed under the terms of the New BSD License.
# The full license can be found in 'LICENSE'.
# Based on: http://egret.psychol.cam.ac.uk/pythonlib/wsgi_gzipper.py

'''the Gzip Module for InPanel Web Server.'''

from gzip import GzipFile
import six


def parse_encoding_header(header):
    ''' Break up the `HTTP_ACCEPT_ENCODING` header into a dict of
        the form, {'encoding-name':qvalue}.
    '''
    encodings = {'identity': 1.0}
    for encoding in header.split(','):
        if encoding.find(';') > -1:
            encoding, qvalue = encoding.split(';')
            encoding = encoding.strip()
            qvalue = qvalue.split('=', 1)[1]
            if qvalue != '':
                encodings[encoding] = float(qvalue)
            else:
                encodings[encoding] = 1
        else:
            encodings[encoding] = 1
    return encodings


def client_wants_gzip(accept_encoding_header):
    ''' Check to see if the client can accept gzipped output, and whether
        or not it is even the preferred method. If `identity` is higher, then
        no gzipping should occur.
    '''
    encodings = parse_encoding_header(accept_encoding_header)
    if 'gzip' in encodings:
        return encodings['gzip'] >= encodings['identity']
    elif '*' in encodings:
        return encodings['*'] >= encodings['identity']
    else:
        return False


class Gzipper(object):
    ''' WSGI middleware to wrap around and gzip all output.
        This automatically adds the content-encoding header.
    '''

    DEFAULT_CONTENT_TYPES = set([
        'text/plain', 'text/html', 'text/css', 'text/javascript', 'text/xml',
        'application/json', 'application/javascript',
        'application/x-javascript', 'application/xml', 'application/xml+rss',
        'application/atom+xml', 'application/xhtml+xml'
    ])

    def __init__(self,
                 app,
                 content_types=DEFAULT_CONTENT_TYPES,
                 compresslevel=6):
        self.app = app
        self.content_types = content_types
        self.compresslevel = compresslevel

    def __call__(self, environ, start_response):
        ''' Do the actual work. If the host doesn't support gzip
            as a proper encoding,then simply pass over to the
            next app on the wsgi stack.
        '''
        if not client_wants_gzip(environ.get('HTTP_ACCEPT_ENCODING', '')):
            return self.app(environ, start_response)

        buf = {'to_gzip': False, 'body': ''}

        def _write(body):
            # for WSGI compliance
            buf['body'] = body

        def _start_response(status, headers, exc_info=None):
            ''' Wrapper around the original `start_response` function.
                The sole purpose being to add the proper headers automatically.
            '''
            for header in headers:
                field = header[0].lower()
                if field == 'content-encoding':
                    # if the content is already encoded, don't compress
                    buf['to_gzip'] = False
                    break
                elif field == 'content-type':
                    ctype = header[1].split(';')[0]
                    if ctype in self.content_types and not (
                            'msie' in environ.get('HTTP_USER_AGENT',
                                                  '').lower()
                            and 'javascript' in ctype):
                        buf['to_gzip'] = True

            buf['status'] = status
            buf['headers'] = headers
            buf['exc_info'] = exc_info
            return _write

        data = self.app(environ, _start_response)

        if buf['status'].startswith('200 ') and buf['to_gzip']:
            data = ''.join(data)
            if len(data) > 200:
                data = self.compress(data)
                headers = buf['headers']
                headers.append(('Content-Encoding', 'gzip'))
                headers.append(('Vary', 'Accept-Encoding'))
                for i, header in enumerate(headers):
                    if header[0] == 'Content-Length':
                        headers[i] = ('Content-Length',
                                      str(len(data) + len(buf['body'])))
                        break
            data = [data]

        _writable = start_response(buf['status'], buf['headers'],
                                   buf['exc_info'])

        if buf['body']:
            _writable(buf['body'])

        return data

    def compress(self, data):
        ''' The `gzip` module didn't provide a way to gzip just a string.
            Had to hack together this. I know, it isn't pretty.
        '''
        gzip_value = six.BytesIO()
        gz_file = GzipFile(mode='wb',
                           compresslevel=self.compresslevel,
                           fileobj=gzip_value)
        gz_file.write(data)
        gz_file.close()
        res = gzip_value.getvalue()
        gzip_value.truncate(0)
        gzip_value.seek(0)
        return res
