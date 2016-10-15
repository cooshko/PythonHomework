#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py
import pickle, sys

with open('data.pickle', 'rb') as f:
    ds = pickle.loads(f.read())


def menu(ds):
        # 循环打印当前层的菜单，除非返回或退出

        # 生成一个字典，序号:当前层的索引
        current_menu = dict()
        id_num = 1
        for key in ds:
            # 序号要转换成字符串，方便以后调用
            current_menu[str(id_num)] = key
            id_num += 1

        # 循环打印菜单
        while True:
            print('=' * 30)
            # 以序号顺序来打印字典（当前菜单层）
            for k in sorted(current_menu.keys()):
                print('%s. %s' % (k, current_menu[k]))
            print('')
            print('(b)返回上一层')
            print('(q)退出')
            pick = input('请选择: ')
            # 用户输入有误
            if pick not in current_menu.keys() and pick not in ['b', 'q']:
                print('找不到你输入的选项，请重新输入')
            elif pick == 'b':
                # 返回上一层菜单
                return
            elif pick == 'q':
                print('正在退出程序')
                sys.exit()
            else:
                # 打印用户的选项
                print('你选择了 ', current_menu[pick])
                # 假如当前层仍是字典类型，代表仍有下级内容，则再次递归调用menu函数
                if isinstance(ds, dict):
                    menu(ds[current_menu[pick]])
                else:
                    print('已是最后一层菜单')


if __name__ == '__main__':
    menu(ds)