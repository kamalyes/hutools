# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  __init__.py
@Time    :  2022/5/27 12:09 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  This library is provided to allow standard python logging to output log data as JSON formatted strings
"""
from .captcha import Captcha, CaptchaPainter
__all__ = ["Captcha", "CaptchaPainter"]
