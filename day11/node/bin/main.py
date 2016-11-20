#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py

import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT)
from day11.node.module.node import Node

if __name__ == '__main__':
    while True:
        hostname = input("请输入当前主机名：").strip()
        if hostname:
            if " " in hostname:
                print("不能包含空格！")
            else:
                break
        else:
            print("不能为空")

    while True:
        group = input("要加入哪个组（留空则为workgroup）：").strip()
        if group:
            if " " in group:
                print("不能包含空格！")
            else:
                break
        else:
            group = "workgroup"
            break

    node = Node("RPC", [group, hostname], hostname)
    node.run()