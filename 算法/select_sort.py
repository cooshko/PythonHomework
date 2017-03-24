#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : select_sort.py
import time
from verify import *


def algorithm(l: list):
    """
    选择排序
    用一个变量记录最小值的下标
    在一开始的时候，这个下标就记录为0
    然后向后进行对比，如果发现有比变量记录的下标的值更小的，则变量记录为这个更小值的下标
    跑完一遍数组后，将记录的位置与起始位置进行互换
    左侧起始位置向左移动，开始下一轮
    :param l:
    :return:
    """
    length = len(l)
    loop_times = 0
    for i in range(length):
        smallest_index = i
        for j in range(i+1, length):
            loop_times += 1
            if l[j] < l[smallest_index]:
                smallest_index = j
        l[smallest_index], l[i] = l[i], l[smallest_index]

    if not isSorted(l):
        print('选择排序失败')
        print(l)
    return l, loop_times, '选择排序'

if __name__ == '__main__':
    l = [324, 12, 564, 43, -32, 1, 0, 132, 99]
    algorithm(l)