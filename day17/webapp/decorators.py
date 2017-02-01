#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.core.urlresolvers import reverse


def check_login(func):
    """
    检查是否已登录两层装饰器
    :param func:
    :return:
    """
    def inner(request, *args, **kwargs):
        # if request.session.get("login", False):
        if request.session.get("user"):
            return func(request, *args, **kwargs)
        else:
            url = reverse("webapp:login")
            print(url)
            return redirect(url)
    return inner


def check_roles(roles: set):
    def wrapper(func):
        def inner(request, *args, **kwargs):
            user_roles = request.session.get("user_roles", [])
            if set(roles).intersection(set(user_roles)):
                return func(request, *args, **kwargs)
            else:
                return HttpResponse("你没有权限访问该页面")
        return inner
    return wrapper


