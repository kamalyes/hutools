# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  mail.py
@Time    :  2022/6/17 12:55 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  Mongodb驱动类
"""

from pymongo import MongoClient
from urllib.parse import quote_plus


class MongoManger(object):
    def __init__(self, host, port=27017, username=None, password=None, db_name=None, set_name=None):
        self.db_name = db_name
        self.set_name = set_name
        uri = "mongodb://%s:%s@%s" % (quote_plus(username), quote_plus(password), host)
        self.conn = MongoClient(uri, port)

        self.refresh_collect()

    def refresh_collect(self, db_name=None, set_name=None):
        if db_name:
            self.db_name = db_name
        if set_name:
            self.set_name = set_name
        if self.db_name:
            self.db = eval("self.conn. %s" % self.db_name)
        if self.set_name:
            self.collect = eval("self.db.%s" % self.set_name)
        return self

    def insert(self, dict_or_list):
        """
        插入
        :param dict_or_list:
        :return:
        """
        return self.collect.insert(dict_or_list)

    def save(self, dict_or_list):
        """
        存储
        :param dict_or_list:
        :return:
        """
        return self.collect.save(dict_or_list)

    def find(self, condition_dict=None):
        """
        查询
        :param condition_dict:
        :return:
        """
        if condition_dict:
            return self.collect.find(condition_dict)
        else:
            return self.collect.find()

    def find_to_list(self, condition_dict=None):
        """
        判断是否多条
        :param condition_dict:
        :return:
        """
        find_cursor = self.find(condition_dict)
        ret_list = []
        for tmpRes in find_cursor:
            tmpRes["_id"] = str(tmpRes["_id"])
            ret_list.append(tmpRes)
        return ret_list

    def find_one(self, condition_dict=None):
        """
        判断是否一条
        :param condition_dict:
        :return:
        """
        if condition_dict:
            return self.collect.find_one(condition_dict)
        else:
            return self.collect.find_one()

    def update(self, query_dict, update_dict, upsert=False, multi=True):
        """
        更新
        :param query_dict:
        :param update_dict:
        :param upsert:
        :param multi:
        :return:
        """
        return self.collect.update(query_dict, update_dict, upsert=upsert, multi=multi)

    def remove(self, query_dict):
        """
        删除
        :param query_dict:
        :return:
        """
        return self.collect.remove(query_dict)
