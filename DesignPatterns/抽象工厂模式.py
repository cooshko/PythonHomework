#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : 抽象工厂模式.py
"""
通常抽象工厂模式用于创建复杂的对象，这种对象由多个其他对象组成
而这些小对象都属于某个特定的系列（family）
"""


class BirdFactory:
    class Bird:
        def fly(self):
            pass

    @classmethod
    def make_bird(cls):
        return cls.Bird()


class EagleFactory(BirdFactory):
    class Bird:
        def fly(self):
            print("老鹰翱翔天际")


class ChickenFactory(BirdFactory):
    class Bird:
        def fly(self):
            print("老鸡飞个毛线")


def create_bird(factory):
    of = factory()
    bird = of.make_bird()   # 调用类方法，生成小类对象
    return bird

if __name__ == '__main__':
    eagle = create_bird(EagleFactory)
    chicken = create_bird(ChickenFactory)
    eagle.fly()
    chicken.fly()
