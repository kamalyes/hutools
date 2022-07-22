# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  system.py
@Time    :  2022/5/2 2:52 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import csv
import json
import os
import platform

import yaml

from .processor import DataHand


class System:
    @staticmethod
    def get_depend_libs(file_path):
        """
        获取第三方依赖架包
        Args:
            file_path:
        Returns:
        Examples:
        """
        if System.is_fdir(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.readlines()
                format_con = ""
                for con in set(content):
                    if not "#" in con:
                        format_con += "".join("`{}`\t".format(con.strip()))
            return format_con

    @staticmethod
    def get_platform_info():
        """
        获取服务运行系统的基础信息
        Returns:
        Examples:
            >>> print(System.get_platform_info())
        """
        return {
            "platform": platform.platform(),  # 获取操作系统名称及版本号
            "machine": platform.machine(),  # 计算机类型
            "node": platform.node(),  # 计算机的网络名称
            "processor": platform.processor(),  # 计算机处理器信息
            "architecture": platform.architecture(),  # 获取操作系统的位数
            "python_version": platform.python_version(),  # 获取操作系统版本号
        }

    @staticmethod
    def get_pool_config(work_spaces_path, target_key=None, environment="pro"):
        """
        获取驱动配置
        Args:
            work_spaces_path:
            environment:
            target_key:
        Returns:
        Examples:
            >>> print(System.get_pool_config(target_key="email"))
        """
        application_file = (
            "application.yaml"
            if environment == "pro"
            else f"application-{environment}.yaml"
        )
        application_file_path = os.path.join(work_spaces_path, application_file)
        if os.path.exists(application_file_path):
            params = System.load_file(application_file_path)
            return params[target_key] if target_key else params
        else:
            raise FileNotFoundError(
                f"未找到application配置文件，请检查以下路径是否正确：{application_file_path}"
            )

    @staticmethod
    def is_fdir(fdir_path, safe_loads=False):
        """
        文件是否存在
        Args:
            fdir_path:
            safe_loads: False 安全模式下可自动创建文件: True
        Returns:
        Examples:
            >>> print(System.is_fdir(fdir_path="Not Fund"))
            >>> print(System.is_fdir(fdir_path="../iutility"))
            >>> print(System.is_fdir(fdir_path="../iutilit", safe_loads=True))
        """
        isfile, isdir = os.path.isfile(fdir_path), os.path.isdir(fdir_path)
        if isfile or isdir:
            return True
        elif safe_loads is False:
            return False
        else:
            with open(fdir_path, "w", encoding="utf-8") as file:
                file.close()
            return System.is_fdir(fdir_path=fdir_path)

    @staticmethod
    def load_file(file_path=None, load_mode="yaml"):
        """
        加载文件
        Args:
            file_path: 文件路径
            load_mode: 加载方式
        Returns:
        """
        with open(file_path, "r", encoding="utf-8") as file:
            if load_mode == "yaml":
                return yaml.safe_load(file)
            elif load_mode == "json":
                try:
                    return json.load(file)
                except json.JSONDecodeError as ex:
                    raise TypeError(
                        "JSONDecodeError:\nfile: %s\nerror: %s" % (file_path, ex)
                    )
            elif load_mode in (".txt", ".py"):
                return file
            elif load_mode == "html":
                return DataHand.format_html_string(file)
            elif load_mode == "csv":
                csv_content_list = []
                with open(file_path, encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        csv_content_list.append(row)
                return csv_content_list

    @staticmethod
    def str_decode(data):
        try:
            data = data.decode()
        except UnicodeDecodeError:
            try:
                data = data.decode(encoding='GBK')
            except UnicodeDecodeError:
                data = data.decode(errors='ignore')
        return data
