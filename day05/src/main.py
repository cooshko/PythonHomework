#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py

"""
该版本没有使用正则
"""

def calc(exp: str):
    if r')' in exp:
        # 如果表达式exp中有括号，则进行如下处理
        # 先将右括号来拆分表达式字符串，取第一个结果，该结果的第一个元素一定包含第一个最里面的表达式，比如"((2*-33"
        # 再用左括号来拆分这个结果第一元素，取新结果的最后一个元素，一定就是最优先计算的表达式了
        parts = exp.split(r')', 1)[0].split(r'(')
        e_str = parts[-1]
        # 使用该最优先计算的表达式去用eval计算得出result
        result = eval(e_str)
        # 准备要替换的原有括号表达式，比如"(2*-33)"，得出新的表达式字符串，如'(-66*(-44+55)/2)'
        old_str = r'(%s)' % e_str
        new_exp = exp.replace(old_str, str(result))
        # 再递归计算新表达式字符串，直至字符串中所有括号表达式被替换掉
        ret = calc(new_exp)
        return ret
    else:
        # exp中没有括号了，直接返回计算结果
        return eval(exp)


if __name__ == '__main__':
    while True:
        print('=' * 30)
        # 样本表达式
        express_example = '((2*-33)*(-44+55)/2)'

        express_str = input("请输入你的运算表达式\n（如果留空，将使用自有样本表达式）：").strip()
        express_str = express_str if express_str else express_example
        print("将要计算的表达式：%s" % express_str)
        # 先将字符串中的空格去掉
        express_str = express_str.replace(' ', '')

        # 显示直接eval的结果
        result_eval = str(eval(express_str))
        result_digui = str(calc(express_str))
        print("直接eval的计算结果：%s" % result_eval)
        print("通过递归计算的结果：%s" % result_digui)
        if result_digui == result_eval:
            print("计算结果相等")
