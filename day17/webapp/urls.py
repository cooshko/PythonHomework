#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^staff/$', views.staff_index, name='staff'),
    url(r'^staff/attendance/$', views.attendance, name='attendance'),
    url(r'^staff/score/$', views.score, name='score'),
    url(r'^staff/manage_student/$', views.manage_student_list, name='manage_student_list'),
    url(r'^staff/manage_student/(\d+)/$', views.manage_student, name='manage_student'),
    url(r'^staff/manage_student/(?P<student_id>\d+)/attendance/(?P<course_id>\d+)/$', views.get_student_attendance_by_course, name='get_student_attendance_by_course'),
    url(r'^staff/consult/$', views.consult, name='consult'),
    url(r'^staff/consult/chat/$', views.consult_chat, name='consult_chat'),
    url(r'^staff/consult/staff_get_msg/$', views.staff_get_msg, name='staff_get_msg'),
    url(r'staff/consult/get_handling/$', views.get_handling, name='get_handling'),
    url(r'staff/consult/save_client_info/$', views.save_client_info, name='save_client_info'),
    url(r'staff/consult/close_a_consult/$', views.close_a_consult, name='close_a_consult'),
    url(r'^staff/follow_up/$', views.follow_up, name='follow_up'),
    url(r'^staff/follow_up/detail/(\d+)/$', views.follow_up_detail, name='follow_up_detail'),
    url(r'^staff/follow_up/detail/new/$', views.new_client, name='new_client'),
    url(r'^staff/follow_up/no_more/$', views.no_more_follow, name='no_more_follow'),
    url(r'^staff/experiencing/$', views.experiencing, name='experiencing'),
    url(r'^staff/exp_course/$', views.exp_course, name='exp_course'),
    url(r'^staff/load_courses/area/(\d+)/$', views.load_courses, name='load_courses'),
    url(r'^student/$', views.student_index, name='student'),
    url(r'^consult/$', views.consult_from_guest, name='consult_from_guest'),
    url(r'^consult/staff_get_msg/$', views.client_get_msg, name='client_get_msg'),
]
