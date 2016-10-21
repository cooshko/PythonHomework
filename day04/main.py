#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, datetime, json, glob, getpass

SEP_ROW = '=' * 60
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(APP_DIR, 'db')
CURRENT_USER = dict()
LOGINED = False
CURRENT_BUY_LOG = list()
INVOICE_DAY = 1
PAYBACK_DAY = 21
MENU_DATA = {
    '家电': [
        ('洗衣机', 1999.0),
        ('冰箱', 3599.0)
    ],
    '汽车': [
        ('Tesla', 1999999.0),
        ('Benz', 359999.0)
    ],
    '电子产品': [
        ('iPhone 7', 6199.0),
        ('iPad', 3000.0)
    ],
    '服饰': [
        ('衣服', 199.9),
        ('裤子', 299.9)
    ],
}


def auth_deco(func):
    """
    装饰器
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        if LOGINED or auth():
            after_guest_login()
            ret = func(*args, **kwargs)
            return ret
    return wrapper


def auth():
    """
    用于认证的函数
    :return:
    """
    global CURRENT_USER, LOGINED
    CURRENT_USER = dict()
    while True:
        print(SEP_ROW)
        user_input = input('请输入账户名称：').strip()
        pass_input = input('密码：').strip()
        # 加载用户信息
        CURRENT_USER = load_user_info(user_input)
        if CURRENT_USER:
            # 如果用户信息存在则进行比对密码
            if not CURRENT_USER.get('locked', True):
                # 如果用户未被锁定
                if pass_input == CURRENT_USER.get('password'):
                    # 密码匹配
                    LOGINED = True
                    return True
                else:
                    print("用户名密码不正确")
                    return False
            else:
                print("该用户已被锁定")
                return False
        elif CURRENT_USER is None:
            # 用户信息文件不存在
            print("该用户不存在。")
            return False
        elif CURRENT_USER is False:
            # 用户文件读取异常
            print('用户状态异常')
            return False


def admin_entry():
    """
    管理员入口
    :return:
    """
    print(SEP_ROW)
    print('''1. 添加账户
2. 修改用户额度
3. 锁定/解锁帐号

(q)退出''')
    global LOGINED
    user_choice = input('请选择：').strip()
    if user_choice == '1':
        # 创建帐号
        if create_guest():
            print("创建成功。")
    elif user_choice == '2':
        # 修改帐号的信用额度
        guest_name = input("请输入账户名称：").strip()
        new_limit_str = input("请输入新的信用额度：").strip()
        try:
            new_limit = float(new_limit_str)
            ret = modify_guest(guest_name, credit_limit=new_limit)
            if ret:
                print('修改完成'.center(64, '*'))
            else:
                print('修改失败'.center(64, '*'))
        except:
            print("您的输入有误")
    elif user_choice == '3':
        # 锁定、解锁用户
        guest_name = input("请输入账户名称：").strip()
        locked_str = input("(l)锁定帐号   (u)解锁帐号 ：").strip()
        if locked_str == 'l':
            modify_guest(guest_name, locked=True)
        elif locked_str == 'u':
            ret = modify_guest(guest_name, locked=False)
            if ret:
                print('修改完成'.center(64, '*'))
            else:
                print('修改失败'.center(64, '*'))
        else:
            print("您的输入有误")
    elif user_choice == 'q':
        LOGINED = False
        return
    else:
        print("你的输入有误，请重新输入")


def load_user_info(username: str):
    """
    :param username: 接收用户名
    :return: 用户字典，如果文件不存在返回None，如果读取、转换异常则返回False
    """
    user_json_file = os.path.join(DB_DIR, username + '.json')
    if os.path.isfile(user_json_file):
        # 如果用户信息文件存在则尝试读取
        try:
            with open(user_json_file) as f:
                user_info = json.load(f)
                return user_info
        except:
            return False
    else:
        # 用户文件不存在
        return None


def cash_from_credit():
    """
    提现
    :return:
    """
    print(SEP_ROW)
    while True:
        print("你现有可用额度%.2f" % CURRENT_USER['credit_available'])
        cash_str = input('请输入你想提现金额（需收取5%手续费）：').strip()
        if cash_str:
            cash = float(cash_str)
            cost = cash * 0.05
            total = cash + cost
            if 0 < total <= CURRENT_USER['credit_available']:
                # 提现金额加上手续费在可用额度范围内
                confirm = input("提现：%.2f  手续费：%.2f，确认输入yes：" % (cash, cost))
                if confirm != 'yes':
                    return
                CURRENT_USER['credit_available'] -= total
                wallet_before = CURRENT_USER['wallet']
                CURRENT_USER['wallet'] += cash
                atm_log(action='提现', amount=cash, merchant='ATM')
                atm_log(action='提现手续费', amount=cost, merchant='ATM')
                save_user(CURRENT_USER)
                print("提现成功！提现前现金：%.2f， 提现后现金%.2f" % (wallet_before, CURRENT_USER['wallet']))
                return True
            elif total > CURRENT_USER['credit_available']:
                # 提现金额加上手续费超出了额度
                print("提现金额加手续费共%.2f，超出了你可用额度，请重新输入。" % total)
            else:
                # 用户输入了0或负数
                print("你输入的格式有误，请重新输入")
        else:
            return False


def pay_by_credit_card(total_amount):
    """
    信用卡消费接口
    :param total_amount:
    :return: 成功扣费则记录日志并返回True，否则返回False
    """
    if total_amount <= 0:
        raise ValueError('结算金额不能小于等于0')
    if total_amount < CURRENT_USER['credit_available']:
        CURRENT_USER['credit_available'] -= total_amount
        atm_log(action="消费", amount=total_amount, merchant="商城")
        shopping_log(total_amount)
        save_user(CURRENT_USER)
        return True
    else:
        print("没有足够的可用额度")
        return False


def settle_invoice_manually():
    """
    人手操作信用卡还款
    :return:
    """
    while True:
        print("本期应还款 %.2f" % CURRENT_USER.get('invoice_amount', 0))
        pay_amount_str = input("请输入你要还款的金额（留空则返回）：").strip()
        if pay_amount_str:
            pay_amount = float(pay_amount_str)
            if CURRENT_USER['wallet'] >= pay_amount:
                # 钱包里有足够的钱，扣减现金和应付金额
                CURRENT_USER['wallet'] -= pay_amount
                CURRENT_USER['invoice_amount'] -= pay_amount
                CURRENT_USER['credit_available'] += pay_amount
                save_user(CURRENT_USER)
                atm_log(action='还款', amount=pay_amount, merchant='ATM')
                return True
            else:
                # 钱包里没有足够的钱
                print("余额不足，请重新输入")
        else:
            return False


def settle_invoice_automaticly(guest: dict):
    # 自动还款
    invoice_amount = guest.get('invoice_amount', 0)
    wallet = guest.get('wallet', 0)
    if wallet >= invoice_amount:
        # 够钱
        kv = {
                'invoice_amount': 0,
                'wallet': wallet - invoice_amount,
                'credit_available': CURRENT_USER['credit_available'] + invoice_amount
             }
        guest.update(kv)
        atm_log(guest=guest, action='自动还款', amount=invoice_amount, merchant='ATM')
        return True
    else:
        # 不够钱
        return False


def trans_money():
    """
    转账
    :return:
    """
    while True:
        print("转 账".center(60, '='))
        recv_person = input("请输入对方帐号名称（留空则返回）：").strip()
        if recv_person:
            if os.path.isfile(os.path.join(DB_DIR, recv_person + '.json')):
                rp = load_user_info(recv_person)
                if rp:
                    amount_str = input("请输入要转账的金额：").strip()
                    amount = float(amount_str)
                    if 0 < amount <= CURRENT_USER['wallet']:
                        CURRENT_USER['wallet'] -= amount
                        rp['wallet'] += amount
                        atm_log(action="转出", amount=-1 * amount, merchant=recv_person)
                        atm_log(action="转入", amount=amount, merchant=CURRENT_USER['name'], guest=rp)
                        save_user(CURRENT_USER)
                        print("转账成功！")
                        return True
                    elif amount <= 0:
                        print("你输入有误，请重新输入")
                        continue
                    else:
                        print("你的帐号余额不足，无法完成转账")
                        return False
                else:
                    print("对方帐号存在异常，无法完成转账")
                    return False
            else:
                print("你输入的帐号不存在")
        else:
            return False


def display_atm_log(limit=10):
    """
    查看ATM日志
    limit参数用于接收要显示日志记录的数量
    默认10条
    :return:
    """
    if CURRENT_USER.get('atm_log'):
        print(SEP_ROW)
        print("%-20s %-20s %-20s %-20s" % ("交易日期", "类型", "金额", "对方帐号"))
        for record in CURRENT_USER['atm_log'][0:limit]:
            print("%-20s %-20s %-20.2f %-20s" % (record[0], record[1], float(record[2]), record[3]))
    else:
        print("没有任何操作记录".center(60, '*'))
    input("按回车返回")


def atm_log(*args, **kwargs):
    """
    记录atm操作日志
    :return:
    """
    log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    action = kwargs.get('action', '未知操作')
    merchant = kwargs.get('merchant', '')
    amount = kwargs.get('amount', 0)
    if action in ['消费',  '提现', '提现手续费']:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        if month == 12:
            p_year = year + 1
            p_month = 1
        else:
            p_year = year
            p_month = month + 1
        p_day = 15
        need_payback_on = datetime.datetime(p_year, p_month, p_day, 23, 59).timestamp()
    if kwargs.get('guest'):
        # 对另外一个客人帐号进行写ATM日志
        p = kwargs.get('guest')
    else:
        # 对当前用户进行写ATM日志
        p = CURRENT_USER
    if not p.get('atm_log'):
        p['atm_log'] = list()
    p['atm_log'].insert(0, [log_time, action, amount, merchant])
    save_user(p)


def guest_entry():
    """
    客人的菜单
    :return:
    """
    global LOGINED
    while True:
        print(SEP_ROW)
        user_choice = input("""
1. 购物
2. ATM

(q)退出
请选择：""")
        if user_choice == '1':
            shopping_menu(MENU_DATA)
        elif user_choice == '2':
            atm_menu()
        elif user_choice == 'q':
            LOGINED = False
            return False


def after_guest_login():
    """
    用户登录后运行的任务，比如生成账单、提醒还款
    :return:
    """
    if CURRENT_USER.get('type') != 'guest':
        return True
    global PAYBACK_DAY
    current_month = datetime.datetime.now().month
    current_day = datetime.datetime.now().day
    invoice_genate_month = CURRENT_USER.get('invoice_genate_month', 0)
    last_month = current_month - 1 if current_month > 1 else 12
    if current_day >= INVOICE_DAY:
        # 每月生成上月账单
        if invoice_genate_month != current_month:
            make_invoice(CURRENT_USER)
            # 如果生成了账单（True），则提醒用户账单，False则视不提醒
        display_invoice(CURRENT_USER)
    if current_day == PAYBACK_DAY:
        # 定期还款
        if settle_invoice_automaticly(CURRENT_USER):
            print("自动还款成功！")

    return True


def display_invoice(guest: dict):
    if guest:
        invoice_amount = guest.get('invoice_amount', 0)
        if invoice_amount:
            print(SEP_ROW)
            print("你本期账单应还款：%.2f" % invoice_amount)


def atm_menu():
    """
    ATM菜单：提现、还款、额度、转账，操作记录
    :return:
    """
    while True:
        print("ATM Menu".center(60, '='))
        print("""1. 提现
2. 还款
3. 账户查询
4. 转账
5. 交易记录
6. 设置信用额度
7. 存款

(b)返回""")
        user_choice = input("请选择：").strip()
        if user_choice == '1':
            cash_from_credit()
        elif user_choice == '2':
            if settle_invoice_manually():
                print("还款成功，你目前的账单金额为 %.2f" % CURRENT_USER.get('invoice_amount', 0))
        elif user_choice == '3':
            print(SEP_ROW)
            print("你当前的\n信用额度上限为：%.2f" % CURRENT_USER.get('credit_limit', 0))
            print("可用额度为 %.2f" % CURRENT_USER.get('credit_available', 0))
            print("现金余额为 %.2f" % CURRENT_USER.get('wallet', 0))
            input("按回车返回")
        elif user_choice == '4':
            # 转账
            trans_money()
        elif user_choice == '5':
            # 查询
            display_atm_log()
        elif user_choice == '6':
            # 设置信用卡额度
            print(SEP_ROW)
            print("你当前的\n信用额度上限为：%.2f" % CURRENT_USER.get('credit_limit', 0))
            new_limit_str = input("设置新信用额度（留空则返回）：").strip()
            if new_limit_str:
                try:
                    new_limit = float(new_limit_str)
                    if new_limit > 0:
                        CURRENT_USER['credit_limit']=new_limit
                        save_user(CURRENT_USER)
                        print("修改额度成功！".center(60, '*'))
                    else:
                        print("请输入大于0的数值")
                except:
                    print("你输入的格式有误".center(60, '*'))
        elif user_choice == '7':
            user_recharge_money()
        elif user_choice == 'b':
            return True


@auth_deco
def select_entry():
    """
    使用装饰器先进行验证
    根据用户类型展示不同的入口
    :return:
    """
    global CURRENT_USER
    user_type = CURRENT_USER.get('type')
    if user_type == 'admin':
        admin_entry()
    elif user_type == 'guest':
        guest_entry()


def create_guest():
    """
    创建新消费帐号
    :return:
    """
    print("创建消费帐号".center(50, '#'))
    while True:
        g_name = input("新帐号名称：").strip()
        if os.path.exists(os.path.join(DB_DIR, g_name + '.json')):
            print('***用户名已存在！***\n请重新输入')
        else:
            break
    g_pass = input("新帐号密码（如留空则默认使用123）：").strip()
    g_pass = g_pass if g_pass else '123'
    g_limit = input("信用额度（留空则默认15000）：").strip()
    g_limit = float(g_limit) if g_limit else 15000
    g_type = 'guest'
    new_guy = True
    g_cart = dict()
    locked = False
    g_wallet = 0
    g_log = list()
    guest_dict = {
        'name': g_name,
        'password': g_pass,
        'credit_limit': g_limit,
        'credit_available': g_limit,
        'cart': g_cart,
        'locked': locked,
        'log': g_log,
        'type': g_type,
        'new_guy': new_guy,
        'wallet': g_wallet
    }
    save_user(guest_dict)
    return True


def modify_guest(guest_name, **kwargs):
    guest = load_user_info(guest_name)
    if guest:
        for k in kwargs:
            guest[k] = kwargs[k]
        save_user(guest)
        return True
    else:
        return False


def save_user(user_dict: dict):
    """
    保存用户状态到文件
    :param user_dict:
    :return:
    """
    fn = os.path.join(DB_DIR, user_dict['name'] + '.json')
    try:
        with open(fn, 'w') as fh:
            json.dump(user_dict, fh)
        return True
    except:
        return False


def shopping_menu(ds):
    product_flag = False
    while True:
        print(SEP_ROW)
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
                            p_price = selected_item[1]
                            cart_update('add', p_name, p_price, p_num)
                            print('已加入购物车：%s x %d' % (p_name, p_num))
                            break
                else:
                    shopping_menu(ds[selected_item])
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


# 展示购物车函数
def cart_display():
    while True:
        # 分割线
        print(SEP_ROW)
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
                print(r'%d. %-10s %10.2f x%2d = %.2f' % (p_id, p_name, p_price, p_num, p_amount))
            print('总金额: %.2f' % total_amount)
            # 如果用户有足够的钱支付，则打印结算选项
            if CURRENT_USER['wallet'] - total_amount >= 0:
                user_action = input('(p)现金付款  (c)信用卡  (u)编辑购物车 (b)返回  请选择：')
                payable_flag = True
            else:
                user_action = input('您的余额不足，(c)信用卡  (u)编辑购物车 (b)返回  请选择：')
                payable_flag = False
            # 判断用户选择
            if payable_flag and user_action == 'p':
                # 付款
                pay_by_cash(total_amount)
                return True
            elif user_action == 'c':
                # 信用卡付款
                ret = pay_by_credit_card(total_amount)
                if ret:
                    return True
                else:
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
            return False


# 更新购物车函数
def cart_update(action, p_name, p_price, p_num):
    # 检查购物车中是否已有该商品，如果没有，则创建一个且件数为0
    CURRENT_USER['cart'][p_name] = CURRENT_USER['cart'].get(p_name, [p_price, 0])
    CURRENT_USER['cart'][p_name][1] += p_num
    # 如果扣减后件数少于等于0，则删除该商品在购物车的记录
    if CURRENT_USER['cart'][p_name][1] <= 0:
        CURRENT_USER['cart'].pop(p_name)
    save_user(CURRENT_USER)


# 显示购买日志
def log_display():
    print(SEP_ROW)
    print('您的购买记录如下：\n\n%-15s %-2s %-2s %-2s %-2s' % ('购买时间', '商品', '单价', '件数', '金额'))
    for log_msg in CURRENT_USER['log']:
        print(log_msg)
    input('任意键返回')


def shopping_log(total_amount: float):
    """
    购物日志
    :param total_amount:
    :return:
    """
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 每一个购物车商品记录为一行日志
    for p_name, p in CURRENT_USER['cart'].items():
        # 记录的内容为购买日期时间、商品名称、数量、单项商品总金额
        log_msg = "%s %s %.2f %d %.2f" % (dt, p_name, p[0], p[1], p[0] * p[1])
        CURRENT_USER['log'].append(log_msg)
        CURRENT_BUY_LOG.append(log_msg)
    # 清空购物车
    CURRENT_USER['cart'] = dict()
    # 保存用户状态
    save_user(CURRENT_USER)
    print('谢谢，您总共消费%.2f元，点击任意键返回' % total_amount)
    input()


def pay_by_cash(total_amount: float):
    """
    现金支付
    :param total_amount:
    :return:
    """
    if CURRENT_USER['wallet'] >= total_amount:
        CURRENT_USER['wallet'] -= total_amount
        shopping_log(total_amount)
        return True
    else:
        return False


def user_recharge_money():
    """
    现金充值函数
    :return:
    """
    user = CURRENT_USER
    print(SEP_ROW)
    print('当前余额：%.2f' % user['wallet'])
    while True:
        recharge = input('请输入你要充值的金额：').strip()
        try:
            user['wallet'] += float(recharge)
            print('充值后余额为：%.2f' % user['wallet'])
            save_user(user)
            return True
        except:
            print('输入格式有误，请重新输入')


def make_invoice(guest: dict):
    """
    出账单
    :return:
    """
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    if month == 1:
        p_month = 12
        p_year = year - 1
    else:
        p_month = month - 1
        p_year = year
    p_prefix = "%d-%02d" % (p_year, p_month)
    # 读取上月atm消费、提现、提现手续费、利息
    p_record_list = list(filter(
        lambda r: str(r[0]).startswith(p_prefix) and r[1] in ['消费', '提现', '提现手续费', '利息'],
        CURRENT_USER.get('atm_log', [])
    ))
    invoice_amount = 0
    if len(p_record_list) > 0:
        for record in p_record_list:
            invoice_amount += float(record[2])
        invoice_amount = abs(invoice_amount)
        guest.update({'invoice_amount': invoice_amount + guest.get('invoice_amount', 0),
                      'invoice_month': p_month,
                      'invoice_genate_month': month
                      })
        save_user(guest)
        return True
    return



if __name__ == '__main__':
    while True:
        select_entry()
