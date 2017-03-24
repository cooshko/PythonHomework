#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : insert_sort.py
import time
from verify import *
"""
插入排序
需求：数组从小到大排序
算法：默认第一个为最小，从第二个元素（假设是n）开始，
跟它左边的元素（m）进行比较，如果左边的比较大，
则双方交换，交换后再n进行左边比较，
直到左侧的元素较小，不发生换位，此轮比较结束
"""


def algorithm(l: list):
    list_length = len(l)
    loop_times = 0
    for i in range(1, list_length):
        left_position = i
        while left_position > 0:
            loop_times += 1
            if l[left_position-1] > l[left_position]:
                l[left_position], l[left_position-1] = l[left_position-1], l[left_position]
                left_position -= 1
            else:
                break

    if not isSorted(l):
        print('插入排序失败')
        print(l)
    return l, loop_times, '插入排序'

if __name__ == '__main__':
    l = [324, 12, 564, 43, -32, 1, 0, 132, 99]
    algorithm(l)
