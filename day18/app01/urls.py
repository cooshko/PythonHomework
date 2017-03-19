#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime
from django.conf.urls import url
from app01 import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^check_exist/$', views.check_exist, name='check_exist'),
    url(r'^verify_code/$', views.verify_code, name='verify_code'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'publish/$', views.publish, name='publish'),
    url(r'posts/$', views.posts, name='posts'),
    url(r'like_post/$', views.like_post, name='like_post'),
    url(r'post_comment/$', views.post_comment, name='post_comment'),
    url(r'get_comments/$', views.get_comments, name='get_comments'),
    url(r'get_online_users/$', views.get_online_users, name='get_online_users'),
]

