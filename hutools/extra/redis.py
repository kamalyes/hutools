# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  cache.py
@Time    :  2021/8/28 10:55 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  Redis封装
"""

import logging
import threading

import redis


class RedisManger(object):
    """
    py2.7, py3.7
    """

    mutex = threading.Lock()  # gevent 里使用线程锁可能有问题
    config = None
    connection_pool = None
    connection_client = None

    def __init__(self, config):
        """
        初始化配置
        :param config:
        """
        self.config = config
        max_conn = 1
        if "max_connections" in self.config:
            max_conn = self.config["max_connections"]
            if max_conn <= 0:
                max_conn = 1
        decode_responses = False
        if "decode_responses" in config:
            decode_responses = config["decode_responses"]
        temp_pool = redis.ConnectionPool(
            host=self.config["host"],
            port=self.config["port"],
            db=self.config["index"],
            password=self.config["auth"],
            encoding=self.config["encoding"],
            max_connections=max_conn,
            decode_responses=decode_responses,
        )
        self.connection_pool = temp_pool
        temp_client = redis.Redis(connection_pool=self.connection_pool)
        self.connection_client = temp_client

    def get_time(self):
        return self.connection_client.time()

    def rpush(self, key, json_text, expired_in_seconds=0):
        """
        在列表中添加一个或多个值
        :param key:
        :param json_text:
        :param expired_in_seconds:
        :return:
        """
        pipe = self.connection_client.pipeline()
        pipe.rpush(key, json_text)
        if expired_in_seconds > 0:
            pipe.expire(key, expired_in_seconds)
        pipe.execute()
        # self.mutex.release()

    def lpush(self, key, json_text, expired_in_seconds=0):
        """
        Lpush 命令将一个或多个值插入到列表头部。
        如果 key 不存在，一个空列表会被创建并执行 LPUSH 操作。
        当 key 存在但不是列表类型时，返回一个错误。
        :param key:
        :param json_text:
        :param expired_in_seconds:
        :return:
        """
        pipe = self.connection_client.pipeline()
        pipe.lpush(key, json_text)
        if expired_in_seconds > 0:
            pipe.expire(key, expired_in_seconds)
        pipe.execute()
        # self.mutex.release()

    def lpop_pipline(self, key, length):
        """
        用于移除并返回列表的第x个元素
        :param key:
        :param length:
        :return:
        """
        i = 0
        poped_items = []
        r = self.connection_client
        # self.mutex.acquire()
        curent_len = r.llen(key)
        if curent_len > 0:
            target_len = 0
            if curent_len > length:
                target_len = length
            else:
                target_len = curent_len
            pipe = r.pipeline()
            while i < target_len:
                pipe.lpop(key)
                i += 1
            temp_poped_items = pipe.execute()
            poped_items = temp_poped_items
        # self.mutex.release()
        return poped_items

    def lpop(self, key):
        """
        移出并获取列表的第一个元素
        :param key:
        :return:
        """
        poped_items = []
        # self.mutex.acquire()
        data = self.connection_client.lpop(key)
        if data:
            poped_items.append(data)
        # self.mutex.release()
        return poped_items

    def rpop_pipline(self, key, length):
        """
        Rpop 命令用于移除列表的最后一个元素，返回值为移除的元素
        :param key:
        :param length:
        :return:
        """
        i = 0
        poped_items = []
        r = self.connection_client
        # self.mutex.acquire()
        curent_len = r.llen(key)
        if curent_len > 0:
            if curent_len > length:
                target_len = length
            else:
                target_len = curent_len
            pipe = r.pipeline()
            while i < target_len:
                pipe.rpop(key)
                i += 1
            temp_poped_items = pipe.execute()
            poped_items = temp_poped_items
        # self.mutex.release()
        return poped_items

    def rpop(self, key):
        """
        移除列表的最后一个元素，返回值为移除的元素
        :param key:
        :return:
        """
        poped_items = []
        data = self.connection_client.rpop(key)
        if data:
            poped_items.append(data)
        # self.mutex.release()
        return poped_items

    def hincrby(self, hash_key, field, amount=1):
        """
        Redis Hincrby 命令用于为哈希表中的字段值加上指定增量值。
        增量也可以为负数，相当于对指定字段进行减法操作。
        如果哈希表的 key 不存在，一个新的哈希表被创建并执行 HINCRBY 命令。
        如果指定的字段不存在，那么在执行命令前，字段的值被初始化为 0 。
        对一个储存字符串值的字段执行 HINCRBY 命令将造成一个错误。
        本操作的值被限制在 64 位(bit)有符号数字表示之内。
        :param hash_key:
        :param field:
        :param amount:
        :return:
        """
        return self.connection_client.hincrby(hash_key, field, amount)

    def llen(self, key):
        """
        用于返回列表的长度。
        如果列表 key 不存在，则 key 被解释为一个空列表，返回 0 。
        如果 key 不是列表类型，返回一个错误。
        :param key:
        :return:
        """
        return self.connection_client.llen(key)

    def hdel(self, key, field):
        """
        用于删除哈希表 key 中的一个或多个指定字段，不存在的字段将被忽略
        :param key:
        :param field:
        :return:
        """
        return self.connection_client.hdel(key, field)

    def hset(self, key, field, value, expired_in_seconds=0):
        """
        用于为哈希表中的字段赋值 。
        如果哈希表不存在，一个新的哈希表被创建并进行 HSET 操作。
        如果字段已经存在于哈希表中，旧值将被覆盖。
        :param key:
        :param field:
        :param value:
        :param expired_in_seconds:
        :return:
        """
        pipline = self.connection_client.pipeline()
        pipline.hset(key, field, value)
        if expired_in_seconds > 0:
            pipline.expire(key, expired_in_seconds)
        pipline.execute()

    def info(self, section=None):
        """
        以一种易于理解和阅读的格式，返回关于 Redis 服务器的各种信息和统计数值
        :param section:
        :return:
        """
        return self.connection_client.info(section)

    def exceed_memory_limits(self):
        result = False
        if "target_max_memory" in self.config.keys():
            target_max_memory = self.config["target_max_memory"]
            redis_info = self.info("memory")
            distance = self.__max_memory_distance(redis_info, target_max_memory)
            if distance and distance <= 0:
                result = True
        return result

    def __max_memory_distance(self, redis_info_dict, target_max):
        # # Memory
        # used_memory:572978192
        # used_memory_human:551.07M
        # used_memory_rss:510640128
        # used_memory_peak:593548568
        # used_memory_peak_human:570.68M
        # used_memory_lua:35850
        # mem_fragmentation_ratio:1.08
        # mem_allocator:jemalloc - 3.6.0
        result = None
        if "used_memory" in redis_info_dict.keys():
            temp_used = int(redis_info_dict["used_memory"])
            temp_used = temp_used / (1024 * 1024)
            result = target_max - temp_used
        else:
            logging.warning("used_memory is not found!")
        return result

    def sadd(self, key, value):
        """
        命令将一个或多个成员元素加入到集合中，已经存在于集合的成员元素将被忽略。
        假如集合 key 不存在，则创建一个只包含添加的元素作成员的集合。
        当集合 key 不是集合类型时，返回一个错误。
        :param key:
        :param value:
        :return:
        """
        return self.connection_client.sadd(key, value)

    def sismember(self, key, value):
        """
        判断成员元素是否是集合的成员
        :param key:
        :param value:
        :return:
        """
        return self.connection_client.sismember(key, value)

    def exists(self, key):
        """
        用于检查给定 key 是否存在
        :param key:
        :return:
        """
        return self.connection_client.exists(key)

    def keys(self, pattern):
        """
        用于查找所有符合给定模式 pattern 的 key
        :param pattern:
        :return:
        """
        return self.connection_client.keys(pattern=pattern)

    def delele(self, key):
        """
        删除键值
        :param key:
        :return:
        """
        self.connection_client.delete(key)

    def scan(self, cursor, match=None, count=50):
        """
        用于迭代集合键中的元素
        :param cursor:
        :param match:
        :param count:
        :return:
         (new_cursor,
            [key1, key2, key3 ...])
        """
        return self.connection_client.scan(cursor=cursor, match=match, count=count)

    def zscan(self, hash_key, cursor, match=None, count=50):
        """
        用于迭代有序集合中的元素（包括元素成员和元素分值）
        :param hash_key: 键值名:
        :param cursor: 游标
        :param match: 匹配的模式
        :param count: 指定从数据集里返回多少元素，默认值为 10
        :return:
         (new_cursor,
            [key1, key2, key3 ...])
        """
        return self.connection_client.zscan(
            hash_key, cursor=cursor, match=match, count=count
        )

    def hscan(self, hash_key, cursor, match=None, count=50):
        """
        HSCAN 命令用于迭代哈希表中的键值对
        :param hash_key: 键值名:
        :param cursor: 游标
        :param match: 匹配的模式
        :param count: 指定从数据集里返回多少元素，默认值为 10
        :return:
         (new_cursor,
            [key1, key2, key3 ...])
        """
        return self.connection_client.hscan(
            hash_key, cursor=cursor, match=match, count=count
        )

    def hmget(self, hash_key, fields_list):
        """
        Redis 中每个 hash 可以存储 232 - 1 键值对（40多亿）
        特别适合用于存储对象
        它是一个 string 类型的 field（字段） 和 value（值） 的映射表
        :param hash_key:
        :param fields_list:
        :return:
        """
        return self.connection_client.hmget(hash_key, fields_list)

    def set(self, key, value, ex=None):
        """
        用于设置给定 key 的值。
        如果 key 已经存储其他值， SET 就覆写旧值，且无视类型
        :param key:
        :param value:
        :param ex:
        :return:
        """
        return self.connection_client.set(key, value, ex)

    def get(self, key):
        """
        获取指定 key 的值。
        :param key:
        :return:
        """
        return self.connection_client.get(key)

    def ttl(self, key):
        """
        查询过期时间
        :param key:
        :return:
        """
        return self.connection_client.ttl(key)

    def close(self):
        if self.connection_pool:
            self.connection_pool.disconnect()
