#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : test.py
import re
host_list = []
group_dict = dict()
with open("hosts.cfg") as f:
    for line in f:
        hostname, url, group = line.split()
        username, password, ip, port = re.findall(r"(.+):(.*)@(.+):(\d+)", url)[0]
        print(username, password, ip, port)

