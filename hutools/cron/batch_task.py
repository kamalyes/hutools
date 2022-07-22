# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  batch_task
@Time    :  2022/6/3 11:55 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""


class BatchTask:
    @staticmethod
    def list_jobs(func_name, context, call_back=False):
        """
        批量任务处理
        Args:
            func_name:
            context:
            call_back: False
        Returns:
        Examples:
            >>> examples = [False, True, 1]
            >>> def test_status(**kwargs):
            ...     return kwargs["example"] is True
            >>> def test_list_jobs(example):
            ...     return  test_status(example=example)
            >>> BatchTask.list_jobs(test_list_jobs, examples)
        """
        accord, no_accord = [], []
        if not isinstance(context, list):
            context = [context]
        for index in context:
            exec_result = func_name.__call__(index)
            if call_back:
                print(exec_result)
            if exec:
                accord.append(index)
            else:
                no_accord.append(index)
        return True if no_accord == [] else (accord, no_accord)
