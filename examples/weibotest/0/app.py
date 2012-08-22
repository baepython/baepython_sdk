#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import web

from framework import WebError
import urls

__author__ = 'Michael Liao'

class PageHandler(object):

    def __init__(self):
        self.mapping = {}
        for s in dir(urls):
            f = getattr(urls, s)
            if callable(f) and getattr(f, 'handler', False):
                self.mapping[getattr(f, '__name__', '')] = f

    def GET(self, path):
        logging.info('GET /%s' % path)
        if path=='':
            path = 'index'
        return self._handle(path)

    def POST(self, path):
        logging.info('POST /%s' % path)
        return self._handle(path)

    def _handle(self, path):
        f = self.mapping.get(path, None)
        if f is None:
            raise web.notfound()
        web.header('Content-Type', 'text/html;charset=utf-8')
        try:
            return f()
        except WebError, e:
            return e.message
        except BaseException, e:
            raise

app = web.application(('/(.*)', 'PageHandler'), globals())

if __name__ == "__main__":
    app.run()
else:
    import sae
    application = sae.create_wsgi_app(app.wsgifunc())
