#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
from django.conf.urls import url
from web_app import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'get-all-books/', views.get_all_books),
    url(r'demo-add/', views.demo_add),
    url(r'add_book/', views.add_book),
]


