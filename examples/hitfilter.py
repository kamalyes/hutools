# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  captcha.py
@Time    :  2022/5/20 2:52 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from hutools.hitfilter import hitfilter

if __name__ == "__main__":
    gfw = hitfilter.DFAFilter()
    gfw.parse("hitfilter_keyword")
    import time

    t = time.process_time()
    print(gfw.filter("法轮功 习近平", "*"))
    print(gfw.filter("外部关键字 996", "*"))
    print(gfw.filter("售假人民币 习近平", "*"))
    print(gfw.filter("vga采集卡", "*"))
    print('Cost is %6.6f' % (time.process_time() - t))
    print(gfw.is_contain_sensitive_key_word('一氧化汞'))


    def test_first_character():
        gfw.add("1989年")
        print(gfw.filter("1989年5月8日", "*"))


    test_first_character()
