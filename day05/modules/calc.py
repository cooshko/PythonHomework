#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import re


def my_calc(exp: str):
    left_num = exp.count('(')
    right_num = exp.count(')')
    if left_num != right_num:
        raise Exception("括号不成对，请检查")
    pattern = "\(([\+\*/\-0-9]+)\)"
    atomic_exps = re.findall(pattern, exp)
    try:
        if len(atomic_exps) > 0:
            # 传入的exp含有括号
            for e_str in atomic_exps:
                result = eval(e_str)
                # 准备要替换的原有括号表达式，比如"(2*-33)"，得出新的表达式字符串，如'(-66*(-44+55)/2)'
                old_str = r'(%s)' % e_str
                exp = exp.replace(old_str, str(result))
                # 再递归计算新表达式字符串，直至字符串中所有括号表达式被替换掉
            return my_calc(exp)
        else:
            # exp中没有括号了，直接返回计算结果
            e_str = exp
            return eval(e_str)
    except:
        raise Exception("表达式%s错误，请检查" % e_str)



def run():
    while True:
        print('=' * 30)
        # 样本表达式
        express_example = '((2*-33)*(-44+55)/2)'

        express_str = input("请输入你的运算表达式\n（如果留空，将使用自有样本表达式）：").strip()
        express_str = express_str if express_str else express_example
        print("将要计算的表达式：%s" % express_str)
        # 先将字符串中的空格去掉
        express_str = express_str.replace(' ', '')
        try:
            result = str(my_calc(express_str))
            print("计算结果：%s" % result)
        except Exception as e:
            print(e)

