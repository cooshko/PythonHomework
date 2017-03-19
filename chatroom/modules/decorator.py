#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : decorator.py


def check_login(func):
    def wrapper(handler, *args, **kwargs):
        if handler.session['is_login']:
            return func(handler, *args, **kwargs)
        else:
            handler.redirect('/login')
    return wrapper


def check_login_ajax(func):
    def wrapper(handler, *args, **kwargs):
        if handler.session['is_login']:
            return func(handler, *args, **kwargs)
        else:
            handler.write({
                'status': 'needlogin',
                'link': '/',
            })
    return wrapper
