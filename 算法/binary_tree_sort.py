#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import time
from verify import *


def algorithm(l: list):
    """
    二叉树排序
    从二叉树的最后的子树开始向树顶一个个子树进行比较，每个子树中的最大数值放到父节点中
    该算法的实现中，先找出数组中所有的父节点，开始进行比较把最大值推到父节点的，
    第一轮结束后，把数组的第一个元素（整个数组中的最大值）与最后一个元素对调（原数组的倒数第一个元素），最后一个元素将不再参与以后的排序
    第一轮结束后，把数组的第一个元素（整个数组中的最大值）与参与排序的数组的最后一个元素对调（相当于原数组的倒数第二个元素），同样不再不再参与以后的排序
    ……
    直到树根下的子树
    :param l:
    :return:
    """
    list_length = len(l)
    loop_times = 0
    for j in range(list_length, 0, -1):
        position = int(j/2-1)
        for i in range(position, -1, -1):
            loop_times += 1
            left_child_index = i*2+1
            right_child_index = i*2+2
            if l[left_child_index] > l[i]:
                l[i], l[left_child_index] = l[left_child_index], l[i]
            if right_child_index < j and l[right_child_index] > l[i]:
                l[i], l[right_child_index] = l[right_child_index], l[i]

        l[0], l[j-1] = l[j-1], l[0]

    # 当进行最后一个堆的比较时，3个数的下标分别是0，1，2，
    # 对应的值分别为x[0]，x[1]，x[2]
    # 最大值在推到x[0]后，x[0]与x[2]交换，那么x[2]变为了三者中最大值
    # 但是，问题来了，程序执行到这里如果退出（因for循环里的i=0了），剩下的x[0]和x[1]就没有进行比较了，
    # 所以在结尾，应当进行这两者的比较换位，才算是整个流程走完
    if l[0] > l[1]:
        l[0], l[1] = l[1], l[0]
    return l, loop_times, '堆排序'

if __name__ == '__main__':
    # l = [0, -32, -5, -92, 1, 10, 12]
    # l = [324, 12, 564, 43, -32, 1, 0, 132, 99, -92, 88, -5, 10, 77, 66]
    import random
    l = list([random.randint(-1000, 1000) for x in range(5000)])
    l = algorithm(l)
    if isSorted(l):
        print('排序成功')
    else:
        print(l)
        print('排序失败')
