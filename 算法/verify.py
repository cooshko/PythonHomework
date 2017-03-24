#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : verify.py


def isSorted(l: list):
    for i in range(1, len(l)):
        if l[i] < l[i-1]:
            print(l[i-1], l[i])
            return False
    return True
