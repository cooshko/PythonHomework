#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : node.py

import os, sys, subprocess, chardet
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT)
from day11.commons.rabbit import Rabbit


class Node(Rabbit):
    def __init__(self, exchange: str, tags: list, nodename: str):
        self.exchange = exchange
        self.tags = tags
        self.nodename = nodename    # 与管理端不同，每个节点都需要设置一个主机名
        super(Node, self).__init__(exchange, tags)

    def run(self):
        print("开始运行。。。")
        self.queue_bind()
        # 侦听要执行的指令
        self.consume(callback=self.callback)

    def callback(self, channel, method, properties, body):
        # 打印收到的指令
        print("Received: %r" % body)
        command = body.decode()
        p = subprocess.Popen(args=command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        header = "================= From %s =================\n" % self.nodename
        out = p.stdout.read()
        err = p.stderr.read()
        result = out if out else err
        result_encodeing = chardet.detect(result)["encoding"]
        result = header + result.decode(encoding=result_encodeing)
        self.publish("fromNodes", result)
        channel.basic_ack(delivery_tag=method.delivery_tag)     # 处理完后确认收到指令


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
