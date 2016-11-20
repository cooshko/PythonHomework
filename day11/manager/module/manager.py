#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : manager.py

import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT)
from day11.commons.rabbit import Rabbit
import threading


class Manager(Rabbit):
    def __init__(self, exchange: str, tags: list):
        self.exchange = exchange
        self.tags = tags
        super(Manager, self).__init__(exchange, tags)

    def run(self):
        # 开启一个线程专门用于显示节点返回的执行结果
        t = threading.Thread(target=self.listen_feedback)
        t.start()

        # 开始交互，用户输入指令的格式为 "NodeTag 命令"
        print('请输入要执行的主机或组，空格后，加上要执行的命令')
        while True:
            inp = input(">> ").strip()
            if inp:
                try:
                    routing_key, command = inp.strip().split(maxsplit=1)
                    # 推送命令
                    self.publish(routing_key=routing_key, body=command)
                except ValueError:
                    print("格式错误，你应输入类似 node1 ipconfig 这种命令")

    def listen_feedback(self):
        # 监听节点返回的执行结果
        self.queue_bind()
        self.consume(callback=self.callback)

    def callback(self, channel, method, properties, body):
        # 打印执行结果，并确认消息
        print(body.decode())
        channel.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == '__main__':
    manager = Manager("RPC", ["fromNodes", ])
    manager.run()
