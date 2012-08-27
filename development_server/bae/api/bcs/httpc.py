# -*- coding: utf-8 -*-

import httplib
import os
import re
import sys
import copy
import mimetypes
from cStringIO import StringIO
from urlparse import urlparse

try:
    from bae.api import logging
except:
    import logging

READ_BODY_TO_MEMORY = 1024*1024 # 1M

###########################################################
# http client
# there is no unicode in this lib 
###########################################################

class FilePartReader:
    def __init__(self, fp, start, length):
        self.fp = fp
        self.fp.seek(start)
        self.length = length

    def read_callback(self, size):
        if self.length == 0: # read all
            return ''
        if self.length > size:
            self.length -= size
            return self.fp.read(size)
        else :
            size = self.length
            self.length -= size
            return self.fp.read(size)
    def read_all(self):
        return self.read_callback(self.length)

class HTTPC:
    ''' define the http client interface'''
    def __init__(self):
        pass
        
    def get(self, url, headers={}):
        raise NotImplementedError()

    def head(self, url, headers={}):
        raise NotImplementedError()

    def put(self, url, body='', headers={}):
        raise NotImplementedError()

    def post(self, url, body='', headers={}):
        raise NotImplementedError()

    def delete(self, url, headers={}):
        raise NotImplementedError()

    def get_file(self, url, local_file, headers={}):
        raise NotImplementedError()

    def put_file(self, url, local_file, headers={}):
        raise NotImplementedError()

    def post_multipart(self, url, local_file, filename='file1', fields={}, headers={}):
        raise NotImplementedError()

    def put_file_part(self, url, local_file, start, length, headers={}):
        raise NotImplementedError()

    def _parse_resp_headers(self, resp_header):
        (status, header) = resp_header.split('\r\n\r\n') [-2] . split('\r\n', 1)
        status = int(status.split(' ')[1])

        header = [i.split(':', 1) for i in header.split('\r\n') ]
        header = [i for i in header if len(i)>1 ]
        header = [[a.strip().lower(), b.strip()]for (a,b) in header ]
        return (status, dict(header) )

class HttplibHTTPC(HTTPC):
    def __init__(self):
        pass
        
    #used by small response (get/put), not get_file
    def request(self, verb, url, data, headers={}):
        response = self.send_request(verb, url, data, headers)
        if verb == 'HEAD':
            response.close()
            resp_body = ''
        else:
            resp_body = response.read()

        rst = { 'status': response.status, 
                'header' : dict(response.getheaders()), 
                'body': resp_body, 
                'body_file': None, 
                }
        return rst

    #used by all 
    def send_request(self, verb, url, data, headers={}):
        logging.info('(%s): (%s)\n' %(verb, url))
        o = urlparse(url)
        host = o.netloc
        path = o.path
        if o.query: 
            path+='?'
            path+=o.query

        if o.scheme == 'https':
            conn = httplib.HTTPSConnection(host)
        else:
            conn = httplib.HTTPConnection(host)
        conn.request(verb, path, data, headers)
        response = conn.getresponse()
        return response

    def get(self, url, headers={}):
        return self.request('GET', url, '', headers)

    def head(self, url, headers={}):
        return self.request('HEAD', url, '', headers)

    def put(self, url, body='', headers={}):
        headers = copy.deepcopy(headers)
        if 'content-length' not in headers:
            headers.update({'content-length': str(len(body)) })
        return self.request('PUT', url, body, headers)

    def post(self, url, body='', headers={}):
        headers = copy.deepcopy(headers)
        if 'Content-Type' not in headers:
            headers.update({'Content-Type': 'application/octet-stream'})
        if 'Content-Length' not in headers:
            headers.update({'Content-Length': str(len(body)) })
        return self.request('POST', url, body, headers)

    def delete(self, url, headers={}):
        return self.request('DELETE', url, '', headers)

    def get_file(self, url, local_file, headers={}):
        response = self.send_request('GET', url, '', headers)
        fout = open(local_file, 'wb')
        CHUNK = 1024*256
        while  True:
            data = response.read(CHUNK)
            if not data:
                break
            fout.write(data)
        fout.close()
        rst = { 'status':  response.status, 
                'header' : dict(response.getheaders()), 
                'body':    None, 
                'body_file': local_file, 
                }
        return rst

    def put_file(self, url, local_file, headers={}):
        return self.put(url, open(local_file, 'rb').read(), headers)

    def post_multipart(self, url, local_file, filename='file1', fields={}, headers={}):
        headers = copy.deepcopy(headers)
        if local_file and filename:
            f = (filename, os.path.basename(local_file), open(local_file, 'rb').read())
            f_list = [f]
        else:
            f_list = []
        content_type, body = encode_multipart_formdata(fields.items(), f_list)
        headersnew = { 'Content-Type' : content_type,
                'Content-Length': str(len(body))}
        headers.update(headersnew)
        return self.post(url, body, headers) 

    def put_file_part(self, url, local_file, start, length, headers={}):
        logging.warn('it is a tragedy to use `put_file_part` by httplib , YoU NeeD pycurl installed! ')
        data = FilePartReader(open(local_file, 'rb'), start, length).read_all()
        return self.put(url, data, headers)

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % _get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY                                                                                             
    return content_type, body

def _get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

__all__ = ['HttplibHTTPC']

