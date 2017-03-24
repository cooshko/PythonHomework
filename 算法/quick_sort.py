#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : quick_sort.py

from verify import *

quick_loop_times = 0


def algorithm(l: list, *args, **kwargs):
    global quick_loop_times
    left = kwargs.get('left', 0)
    right = kwargs.get('right', len(l)-1)
    if right > left:
        i = left
        j = right
        x = l[i]    # 流程开始前，取一个基数，这里取给定的左下标
        while i < j:
            while i < j and l[j] >= x:
                quick_loop_times += 1
                # 从给定的数组，右下标往左移动并比较，
                # 如果下标的值比基数大，则右下标继续往左移动，
                j -= 1
                # 直到以下两种情况之一停止
                # ·右下标的值小于基数
                # ·i和j相等了，即左右下标碰头了

            if i < j:
                # 如果发现右下标的值比基数小于等于基数
                # 将右下标的值复制到左下标处（即i），然后左下标往右移动一位
                l[i] = l[j]
                i += 1

            while i < j and l[i] <= x:
                quick_loop_times += 1
                # 左下标开始移动
                i += 1
                # 直到以下两种情况之一停止
                # ·左下标的值大于基数
                # ·i和j相等了，即左右下标碰头了

            if i < j:
                # 发现左下标的值大于等于基数
                # 将左下标的值
                l[j] = l[i]

        l[i] = x    # 流程最后，将基数复制到左下标处
        algorithm(l, left=left, right=i - 1)
        algorithm(l, left=i + 1, right=right)

        return l, quick_loop_times, '快速排序'


if __name__ == '__main__':
    # l = [0, -32, -5, -92, 1, 10, 12]
    l = [324, 12, 564, 99, 43, 99, -32, 1, 0, 132, 99, -92, 88, -5, 10, 77, 66]
    # import random
    # l = list([random.randint(-1000, 1000) for x in range(5000)])
    ret_l, loop_times, name = algorithm(l)
    print(ret_l)
    print(loop_times)
    print(quick_loop_times)
    # if isSorted(l):
    #     print('排序成功')
    # else:
    #     print(l)
    #     print('排序失败')
