#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py

import json, sys, os, datetime
APP_ABS_PATH = os.path.dirname(os.path.abspath(__file__))
CURRENT_USER = dict()
# 华丽的分割线
sep_row = '=' * 50


# 根据用户名（字符串），从文件读取用户信息，如果没有文件或者无法转换都会返回False
def load_user_info(user: str):
    try:
        if not user.strip():
            raise Exception
        fp = os.path.join(APP_ABS_PATH, user + '.json')
        with open(fp) as fh:
            ret = json.load(fh)
        return ret
    except Exception as e:
        return False


# 将用户信息（字典），保存到文件中去，以便以后读取
def save_user_info(user: dict):
    if not user:
        return False
    fp = os.path.join(APP_ABS_PATH, user['name'] + '.json')
    try:
        with open(fp, 'w') as fh:
            json.dump(user, fh)
        return True
    except:
        return False


# 打印菜单并让用户进行选择
def shopping_menu(user: dict, ds):
    product_flag = False
    while True:
        print(sep_row)
        # ds为字典类型代表上级菜单
        if isinstance(ds, dict):
            menu_list = [key for key in sorted(ds.keys())]
            for menu_id, menu_item in enumerate(menu_list):
                print(menu_id, menu_item)
        # ds为列表类型，代表商品
        elif isinstance(ds, list):
            product_flag = True
            menu_list = ds
            for menu_id, menu_item in enumerate(menu_list):
                print(menu_id, menu_item[0], menu_item[1])
        else:
            raise Exception('ds type wrong')
        print('''
(c)购物车
(q)退出
(b)返回''')
        user_choice = input('请选择：').strip()
        # 用户输入的是数字
        if user_choice.isdigit():
            user_choice = int(user_choice)
            selected_item = menu_list[user_choice]
            if product_flag:
                while True:
                    p_num = input('你选择的是 %s，请输入件数：' % selected_item[0])
                    if p_num.isdigit():
                        p_num = int(p_num)
                        p_name = selected_item[0]
                        p_price = int(selected_item[1])
                        cart_update('add', p_name, p_price, p_num)
                        print('已加入购物车：%s x %d' % (p_name, p_num))
                        break
            else:
                shopping_menu(user, ds[selected_item])
        # 如果用户输入的不是数字
        elif user_choice in ['q', 'b', 'c']:
            if user_choice == 'q':
                exit()
            elif user_choice == 'b':
                return
            elif user_choice == 'c':
                cart_display()
        else:
            print('你的输入有误，请重新选择')


# 充值函数
def user_recharge_money():
    user = CURRENT_USER
    print(sep_row)
    if user:
        print('当前余额：%d' % user['wallet'])
    else:
        user['wallet'] = 0
    while True:
        recharge = input('请输入你要充值的金额：').strip()
        if recharge.isdigit():
            user['wallet'] += int(recharge)
            print('充值后余额为：%d' % user['wallet'])
            try:
                save_user_info(user)
            except:
                pass
            return True
        else:
            print('输入格式有误，请重新输入')


# 用户支付
def user_pay(total_amount: int):
    pass


# 展示购物车函数
def cart_display():
    while True:
        # 分割线
        print(sep_row)
        # 如果当前用户购物车中有商品
        if CURRENT_USER['cart']:
            # 结算总金额
            total_amount = 0
            # 对购物车的商品名称进行排序，然后枚举并打印序号和商品明细
            for p_id, p_name in enumerate(sorted(CURRENT_USER['cart'].keys())):
                p_price = CURRENT_USER['cart'][p_name][0]
                p_num = CURRENT_USER['cart'][p_name][1]
                p_amount = p_price * p_num
                total_amount += p_amount
                print(r'%d. %-10s %10d x%2d = %d' % (p_id, p_name, p_price, p_num, p_amount))
            print('总金额: %d' % total_amount)
            # 如果用户有足够的钱支付，则打印结算选项
            if CURRENT_USER['wallet'] - total_amount >= 0:
                user_action = input('(p)付款  (u)编辑购物车  请选择：')
                payable_flag = True
            else:
                user_action = input('您的余额不足，(r)充值  (u)编辑购物车  请选择：')
                payable_flag = False
            # 判断用户选择
            if payable_flag and user_action == 'p':
                # 付款
                pass
            elif not payable_flag and user_action == 'r':
                # 充值
                user_recharge_money()
            elif user_action == 'u':
                # 更新购物车
                pass
            else:
                print('您的输入有误，请重新输入')
                continue
        # 购物车中没有商品，任意键返回
        else:
            print('你的购物车空空如也\n\n(b)返回')
            input()
            return


# 更新购物车函数
def cart_update(action, p_name, p_price, p_num):
    # 检查购物车中是否已有该商品，如果没有，则创建一个且件数为0
    CURRENT_USER['cart'][p_name] = CURRENT_USER['cart'].get(p_name, [p_price, 0])
    # 往购物车加入商品
    if action == 'add':
        CURRENT_USER['cart'][p_name][1] += p_num
    # 减少购物车中的商品数量
    elif action == 'minus':
        CURRENT_USER['cart'][p_name][1] -= p_num
        # 如果扣减后件数少于等于0，则删除该商品在购物车的记录
        if CURRENT_USER['cart'][p_name][1] <= 0:
            CURRENT_USER['cart'].pop(p_name)
    else:
        pass
    # 每次更新完购物车，都需要保存到文件中去，即使程序退出了，下次再次登陆，也能恢复购物车记录
    save_user_info(CURRENT_USER)


# 程序入口
if __name__ == '__main__':
    # 用户输入身份信息
    username = input('请问您是? ').strip()

    print(sep_row)
    # 从文件读取用户信息
    CURRENT_USER = load_user_info(username)
    # 如果是老客户，打印欢迎消息和余额
    if CURRENT_USER:
        print(r'欢迎回来 %s，您的余额是%d' % (CURRENT_USER['name'], CURRENT_USER['wallet']))
    # 如果是新客户，则初始化其数据，并让用户充值，最后保存到用户对应的文件
    else:
        print('你是新顾客')
        CURRENT_USER = dict()
        user_recharge_money()
        CURRENT_USER['name'] = username
        CURRENT_USER['log'] = []
        CURRENT_USER['cart'] = dict()
        save_user_info(CURRENT_USER)

    # 循环开始
    # 打印入口
    while True:
        print(sep_row)
        entry_choice = input(r'''请选择您要做什么:
1. 购物
2. 充值

(q) 退出
请选择：''')
        # 用户输入q，则退出程序
        if entry_choice == 'q':
            exit()
        # 用户输入1，则进行购物
        elif entry_choice == '1':
            # 加载菜单数据
            with open(os.path.join(APP_ABS_PATH, 'menu.json')) as f:
                menu_ds = json.load(f)
                shopping_menu(CURRENT_USER, menu_ds)
        # 如果输入2，则进行充值
        elif entry_choice == '2':
            user_recharge_money()
        # 用户的其他输入视为错误，并要求重新输入
        else:
            print('您的输入有误，请重新输入')
