#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

from tornado import ioloop, web
from tornado.options import parse_command_line
from conf import config
import urls

app = web.Application(urls.handlers, **config.app_settings)
if __name__ == '__main__':
    parse_command_line()
    app.listen(config.server_port)
    print(r'http://127.0.0.1:%d' % config.server_port)
    print(r'您也可以观看DEMO: http://183.63.156.214:%d' % config.server_port)
    ioloop.IOLoop.current().start()
