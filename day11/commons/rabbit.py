#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : rabbit.py

import pika, configparser, os


class Rabbit(object):
    def __init__(self, exchange: str, tags: list):
        # 建立连接、生成队列名称，声明exchange
        self.tags = tags
        self.exchange = exchange
        cp = configparser.ConfigParser()
        conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conf", "rabbit.conf")
        cp.read(conf_file)
        self.ip = cp['rabbit']['ip']
        self.port = int(cp['rabbit']['port'])
        self.username = cp['rabbit']['username']
        self.password = cp['rabbit']['password']
        cred = pika.PlainCredentials(self.username, self.password)
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(host=self.ip, port=self.port, credentials=cred))
        self.channel = self.conn.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.exchange_declare(exchange=self.exchange, type="direct")
        self.queue_name = self.generate_queue_name()    # 监听的队列
        
    def generate_queue_name(self):
        # 返回随机生成的一个队列
        result = self.channel.queue_declare(exclusive=True)
        return result.method.queue

    def queue_bind(self):
        # 绑定队列、exchange、routing_key
        for tag in self.tags:
            self.channel.queue_bind(exchange=self.exchange,
                                    routing_key=tag,
                                    queue=self.queue_name)

    def publish(self, routing_key, body):
        # 发布消息
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=routing_key,  # 不再指定队列名称，但仍需指定一个空字符串
                                   body=body,  # 具体的消息内容
                                   properties=pika.BasicProperties(delivery_mode=2))  # 此消息需要持久化

    def consume(self, callback):
        # 循环接收消息，并根据callback去处理消息
        self.channel.basic_consume(queue=self.queue_name,  # 指定接收队列名称
                                   no_ack=False,  # 确认该消息，ack功能用于防止消息丢失
                                   consumer_callback=callback)  # 收到的数据，使用回调函数去处理，这里使用上方定义的callback函数
        self.channel.start_consuming()

if __name__ == '__main__':
    rabbit = Rabbit("RPC", ["test", ])
