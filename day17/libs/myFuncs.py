#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime, hashlib


def to_md5(s: str):
    ret = None
    if s:
        m = hashlib.md5()
        m.update(s.encode(encoding='utf-8'))
        ret = m.hexdigest()
    return ret


