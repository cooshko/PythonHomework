#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : app.py
import threading, random, time
# 以下导入所有算法
import insert_sort
import bubble_sort
import select_sort
import shell_sort
import binary_tree_sort
import quick_sort

# 导入验证排序是否成功的函数
import verify


def mission(func, l):
    """
    该函数将被启动为线程
    :param func: 各个排序算法的函数入口
    :param l: 要排序的数组
    :return:
    """
    new_list = l.copy()     # 浅拷贝到新的数组，避免影响其他线程的调用原数组
    start = time.time()
    ret_list, loop_times, func_name = func(new_list)    # 我定义了每种算法都必须返回这三个元素，分别是排序完的数组，循环次数，算法的名称
    end = time.time()
    if verify.isSorted(ret_list):
        """ 验证排序完的数组是有序的 """
        print('%s 共循环了%d次，耗时%f' % (func_name, loop_times, end-start))
    else:
        print('%s 失败')


if __name__ == '__main__':
    test_times = 3000
    ran_list = list([random.randrange(0-test_times, test_times) for i in range(test_times)])    # 生成待测试的随机数组

    t_list = []  # 存放线程的数组
    for adapter in [insert_sort, bubble_sort, select_sort, shell_sort, binary_tree_sort, quick_sort]:
        t = threading.Thread(target=mission, kwargs={'func': adapter.algorithm, 'l': ran_list})
        t.start()
        t_list.append(t)

    for t in t_list:
        t.join()

