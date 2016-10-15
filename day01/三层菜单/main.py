#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py
import pickle, sys

with open('data.pickle', 'rb') as f:
    ds = pickle.loads(f.read())

def menu(ds):
    # 菜单最底层的数据是集合类型，当ds不是集合，则代表还在菜单当中
    if not isinstance(ds, set):
        # 循环打印当前层的菜单，除非返回或退出
        # 生成一个列表，每个列表值都是ds字典的
        current_menu = dict()
        for i in len(ds):
            current_menu[i+1] = ds[i]
        while True:
            for i in range(len(current_menu)):
                print('%d. %s' % (i, current_menu))



if __name__ == '__main__':
    print(ds)