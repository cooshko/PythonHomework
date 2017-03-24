#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : bubble.py

import time
from verify import *


def algorithm(l: list):
    """
    数值两两相比，大的放前面，小的放后面
    :param l:
    :return:
    """
    length = len(l)
    loop_times = 0
    for i in range(1, length-2):
        for j in range(length-1):
            loop_times += 1
            if l[j] > l[j+1]:
                l[j], l[j+1] = l[j+1], l[j]
    return l, loop_times, '冒泡排序'

if __name__ == '__main__':
    l = [324, 12, 564, 43, -32, 1, 0, 132, 99]
    algorithm(l)