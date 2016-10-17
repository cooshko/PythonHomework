#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py

import json,  os, datetime
APP_ABS_PATH = os.path.dirname(os.path.abspath(__file__))
CURRENT_USER = dict()
CURRENT_BUY_LOG = []
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
(c)购物车  (r)购买记录  (q)退出  (b)返回''')
        user_choice = input('请选择：').strip()
        # 用户输入的是数字
        if user_choice.isdigit():
            user_choice = int(user_choice)
            if user_choice < len(menu_list):
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
            else:
                print('你的输入超出范围，请重新选择')
                input()
        # 如果用户输入的不是数字
        elif user_choice in ['q', 'b', 'c', 'r']:
            if user_choice == 'q':
                user_leave()
            elif user_choice == 'b':
                return
            elif user_choice == 'c':
                cart_display()
            elif user_choice == 'r':
                log_display()
        else:
            print('你的输入有误，请重新选择')
            input()


# 充值函数
def user_recharge_money():
    user = CURRENT_USER
    print(sep_row)
    if user['new_guy']:
        user['wallet'] = 0
        user['new_guy'] = False
    else:
        print('当前余额：%d' % user['wallet'])
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
    # 扣钱
    CURRENT_USER['wallet'] -= total_amount
    # 写入日志
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 每一个购物车商品记录为一行日志
    for p_name, p in CURRENT_USER['cart'].items():
        # 记录的内容为购买日期时间、商品名称、数量、单项商品总金额
        log_msg = "%s %s %d %d %d" % (dt, p_name, p[0], p[1], p[0]*p[1])
        CURRENT_USER['log'].append(log_msg)
        CURRENT_BUY_LOG.append(log_msg)
    # 清空购物车
    CURRENT_USER['cart'] = dict()
    # 保存用户状态
    save_user_info(CURRENT_USER)
    print('谢谢，您总共消费%d元，点击任意键返回' % total_amount)
    input()


# 用户想离开，打印当次购买记录
def user_leave():
    global CURRENT_BUY_LOG
    if CURRENT_BUY_LOG:
        print('多谢惠顾，您本次的购物清单如下')
        print('您的购买记录如下：\n\n%-15s %-2s %-2s %-2s %-2s' % ('购买时间', '商品', '单价', '件数', '金额'))
        for log_msg in CURRENT_BUY_LOG:
            print(log_msg)
        CURRENT_BUY_LOG = []
    exit()


# 用户验证函数
def user_auth():
    global CURRENT_USER
    print(sep_row)
    while True:
        username_input = input('用户名：').strip()
        # 从文件读取用户信息
        CURRENT_USER = load_user_info(username_input)
        # 如果是老客户，打印欢迎消息和余额
        if CURRENT_USER:
            password_input = input('密码：')
            if password_input == CURRENT_USER['password']:
                print(r'欢迎回来 %s，您的余额是%d' % (CURRENT_USER['name'], CURRENT_USER['wallet']))
                return True
            else:
                print('您输入密码有误，请重新输入')
        # 如果是新客户，则初始化其数据，并让用户充值，最后保存到用户对应的文件
        else:
            print('你是新顾客')
            init_password = input('请输入一个密码作登录用途（如留空，则默认使用123）:')
            CURRENT_USER = dict()
            CURRENT_USER['name'] = username_input
            CURRENT_USER['password'] = init_password if init_password else '123'
            CURRENT_USER['log'] = []
            CURRENT_USER['cart'] = dict()
            CURRENT_USER['new_guy'] = True
            user_recharge_money()
            save_user_info(CURRENT_USER)
            return True


# 展示购物车函数
def cart_display():
    while True:
        # 分割线
        print(sep_row)
        print('您的购物车内有如下物品\n')
        # 如果当前用户购物车中有商品
        if CURRENT_USER['cart']:
            # 结算总金额
            total_amount = 0
            # 商品种类数量
            kind_num = len(CURRENT_USER['cart'])
            # 商品名称列表
            p_list = enumerate(sorted(CURRENT_USER['cart'].keys()))
            # 对购物车的商品名称进行排序，然后枚举并打印序号和商品明细
            for p_id, p_name in p_list:
                p_price = CURRENT_USER['cart'][p_name][0]
                p_num = CURRENT_USER['cart'][p_name][1]
                p_amount = p_price * p_num
                total_amount += p_amount
                print(r'%d. %-10s %10d x%2d = %d' % (p_id, p_name, p_price, p_num, p_amount))
            print('总金额: %d' % total_amount)
            # 如果用户有足够的钱支付，则打印结算选项
            if CURRENT_USER['wallet'] - total_amount >= 0:
                user_action = input('(p)付款  (u)编辑购物车 (b)返回  请选择：')
                payable_flag = True
            else:
                user_action = input('您的余额不足，(r)充值  (u)编辑购物车 (b)返回  请选择：')
                payable_flag = False
            # 判断用户选择
            if payable_flag and user_action == 'p':
                # 付款
                user_pay(total_amount)
                return True
            elif not payable_flag and user_action == 'r':
                # 充值
                user_recharge_money()
                continue
            elif user_action == 'b':
                return
            elif user_action == 'u':
                # 更新购物车
                user_choice = input('请输入商品编号：')
                if user_choice.isdigit():
                    user_choice = int(user_choice)
                    # 用户输入正确
                    if user_choice < kind_num:
                        p_name = sorted(CURRENT_USER['cart'].keys())[user_choice]
                        p_price = CURRENT_USER['cart'][p_name][0]
                        p_num = CURRENT_USER['cart'][p_name][1]
                        print('您选择的是 %s ，购物车中有%d件' % (p_name, p_num))
                        adjust_offset = input('请输入加减件数（比如 +1 或者 -1）：').strip()
                        try:
                            adjust_offset = int(adjust_offset)
                            if adjust_offset > 0:
                                cart_update('add', p_name, p_price, adjust_offset)
                            elif adjust_offset < 0:
                                cart_update('minus', p_name, p_price, adjust_offset)
                            continue
                        except:
                            pass
            print('您的输入有误，请重新输入')
        # 购物车中没有商品，任意键返回
        else:
            print('空空如也\n\n(b)返回')
            input()
            return


# 更新购物车函数
def cart_update(action, p_name, p_price, p_num):
    # 检查购物车中是否已有该商品，如果没有，则创建一个且件数为0
    CURRENT_USER['cart'][p_name] = CURRENT_USER['cart'].get(p_name, [p_price, 0])
    CURRENT_USER['cart'][p_name][1] += p_num
    # 如果扣减后件数少于等于0，则删除该商品在购物车的记录
    if CURRENT_USER['cart'][p_name][1] <= 0:
        CURRENT_USER['cart'].pop(p_name)
    save_user_info(CURRENT_USER)


# 显示购买日志
def log_display():
    print(sep_row)
    print('您的购买记录如下：\n\n%-15s %-2s %-2s %-2s %-2s' % ('购买时间', '商品', '单价', '件数', '金额'))
    for log_msg in CURRENT_USER['log']:
        print(log_msg)
    input('任意键返回')

# 程序入口
if __name__ == '__main__':
    # 验证用户
    user_auth()

    # 循环开始
    # 打印入口
    while True:
        print(sep_row)
        entry_choice = input(r'''请选择您要做什么:
1. 购物
2. 充值

(q)退出  请选择：''')
        # 用户输入q，则退出程序
        if entry_choice == 'q':
            user_leave()
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
