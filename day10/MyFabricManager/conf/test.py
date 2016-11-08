#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : test.py
host_list = []
group_dict = dict()
with open("hosts.cfg") as f:
    for line in f:
        hostname, ip_port, group = line.split()
        ip = ip_port.split(":")[0]
        port = ip_port.split(":")[1]
        host = {'hostname': hostname, 'ip': ip, 'port': port}
        if group in group_dict:
            group_dict[group].append(host)
        else:
            group_dict[group] = [host, ]
        host_list.append(host)
