#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : hill_sort.py
import time
from verify import *
import insert_sort


def algorithm(l: list):
    """
    希尔排序
    先计算一个最大步长，相当于列表长度的一半，
    然后步长依次递减，进行左右下标的两两比较
    右下标 = 左下标 + 步长
    每次都将 左下标 与 右下标 的值进行比较，
    如果左下标的值比右下标的大，则互换位置（也可以改为比小的）
    直到步长减到1，得出一个“接近有序”的列表，
    最后进行一次插入排序
    :param l:
    :return:
    """
    list_length = len(l)
    step = int(list_length / 2)
    loop_times = 0
    while step >= 1:
        for i in range(list_length - step):
            loop_times += 1
            if l[i] > l[i + step]:
                l[i], l[i + step] = l[i + step], l[i]
        step = int(step/2)   # 步长为原先的一半

    ret, insert_loop, _ = insert_sort.algorithm(l)
    if not isSorted(ret):
        print('希尔排序失败')
        print(ret)
    return ret, loop_times + insert_loop, '希尔排序'

if __name__ == '__main__':
    l = [9, 88, 1, 8, 22, 9, 31, -5, 26, 45, 3, 6, 2, 11, 19]
    algorithm(l)
