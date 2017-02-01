#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime
from django import template
from webapp.models import *

register = template.Library()


@register.filter(name="get_score")
def get_score(student, course_id):
    cs = student.coursescore_set.filter(course_id=course_id).first()
    if cs:
        score = cs.score
    else:
        score = ""
    return score

