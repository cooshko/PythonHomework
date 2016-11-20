#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : rabbit.py

import pika

class Rabbit(object):
    def __init__(self, exchange: str, tags: list):
        self.tags = tags
        self.exchange = exchange
        cred = pika.PlainCredentials("coosh", "coosh")
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(host="192.168.199.196", credentials=cred))
        self.channel = self.conn.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.exchange_declare(exchange="direct", type="direct")
        self.queue_name = self.generate_queue_name()
        
    def generate_queue_name(self):
        result = self.channel.queue_declare(exclusive=True)
        return result.method.queue  # 随机生成一个队列

    def queue_bind(self):
        for tag in self.tags:
            self.channel.queue_bind(exchange=self.exchange,
                                    routing_key=tag,
                                    queue=self.queue_name)
    