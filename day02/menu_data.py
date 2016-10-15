#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : menu_data.py
import json, os

menu_data = {
    '家电': [
        ('洗衣机', 1999),
        ('冰箱', 3599)
    ],
    '汽车': [
        ('Tesla', 1999999),
        ('Benz', 359999)
    ],
    '电子产品': [
        ('iPhone 7', 6199),
        ('iPad', 3000)
    ],
    '服饰': [
        ('衣服', 199),
        ('裤子', 300)
    ],
}

if  __name__ == '__main__':
    app_abs_path = os.path.dirname(os.path.abspath(__file__))
    fn = os.path.join(app_abs_path, 'menu.json')
    with open(fn, 'w') as f:
        json.dump(menu_data, f)
