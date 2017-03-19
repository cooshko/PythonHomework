#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : json_encoder.py
from datetime import datetime, timedelta
import json


class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            o = o + timedelta(hours=8)
            return o.strftime('%Y-%m-%d %H:%M:%S')
        super(DateTimeJSONEncoder, self).default(o)
