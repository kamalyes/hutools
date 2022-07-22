# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  processor.py
@Time    :  2022/5/1 8:21 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  An XPath for JSON 后置处理
"""
import base64
import hashlib
import json
import re
import sys
import xml.dom.minidom
import xml.etree.ElementTree
from functools import reduce
from itertools import zip_longest
from typing import Text, Dict, Any
from urllib.parse import unquote

from dicttoxml import dicttoxml
from lxml import etree
from six import text_type, binary_type

from hutools.core.xml2dict import Xml2Dict

SINGLE_UPLOAD_LENGTH = 5 * 1024 * 1024 * 1024  # 单次上传文件最大为5GB
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 计算MD5值时,文件单次读取的块大小为1MB


class AttrDict(dict):
    """
    继承自dict，实现可以通过.来操作元素
    Examples:
        >>> attr_dict = AttrDict(data=56999, step=0, s_status='process', status=0)
        >>> print(attr_dict.data)
    """

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __delattr__(self, item):
        self.__delitem__(item)


class DataHand:
    @staticmethod
    def to_str(variable):
        """非字符串转换为字符串"""
        if isinstance(variable, text_type) or isinstance(variable, binary_type):
            return variable
        return str(variable)

    @staticmethod
    def to_unicode(variable):
        """将字符串转为unicode"""
        if isinstance(variable, binary_type):
            try:
                return variable.decode('utf-8')
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError('your bytes strings can not be decoded in utf8, utf8 support only!')
        return variable

    @staticmethod
    def to_bytes(variable):
        """将字符串转为bytes"""
        if isinstance(variable, text_type):
            try:
                return variable.encode('utf-8')
            except UnicodeEncodeError as e:
                raise UnicodeEncodeError('your unicode strings can not encoded in utf8, utf8 support only!')
        return variable

    @staticmethod
    def deep_dict_update(main_dict: Dict[Any, Any], update_dict: Dict[Any, Any]) -> dict[Any, Any]:
        """
        字典更新
        Args:
            main_dict:
            update_dict:

        Returns:

        Examples:
            >>> main_dict = {"a":1, "b":2, "c":{"abc":123}}
            >>> update_dict = {"a":2, "b":5, "c":{"abc":1235678}}
            >>> print(DataHand.deep_dict_update(main_dict, update_dict))

        """
        for key, value in update_dict.items():
            if (
                    key in main_dict
                    and isinstance(main_dict[key], dict)
                    and isinstance(value, dict)
            ):
                DataHand.deep_dict_update(main_dict[key], value)
            else:
                main_dict[key] = value
        return main_dict

    @staticmethod
    def lower_dict_keys(origin_dict: Dict):
        """
        convert keys in dict to lower case
        Args:
            origin_dict: mapping data structure

        Returns:
            dict: mapping with all keys lowered.

        Examples:
            >>> origin_dict = { "Name": "", "Request": "", "URL": "", "METHOD": "", "Headers": "", "Data": ""}
            >>> DataHand.lower_dict_keys(origin_dict)
        """
        if not origin_dict or not isinstance(origin_dict, dict):
            return origin_dict

        return {key.lower(): value for key, value in origin_dict.items()}

    @staticmethod
    def upper_dict_keys(origin_dict: Dict):
        """
        convert keys in dict to lower case
        Args:
            origin_dict: mapping data structure

        Returns:
            dict: mapping with all keys lowered.

        Examples:
            >>> origin_dict = {'name': '', 'request': '', 'url': '', 'method': '', 'headers': '', 'data': ''}
            >>> DataHand.upper_dict_keys(origin_dict)
        """
        if not origin_dict or not isinstance(origin_dict, dict):
            return origin_dict

        return {key.upper(): value for key, value in origin_dict.items()}

    @staticmethod
    def list_to_dict(origin_list):
        """
        list转dict
        :param origin_list: (list) [{"name": "v", "value": "1"},{"name": "w", "value": "2"}]
        :return: dict:{"v": "1", "w": "2"}
        """
        return {item["name"]: item.get("value") for item in origin_list}

    @staticmethod
    def omit_long_data(body, omit_len=512):
        """
        omit too long str/bytes
        Args:
            body:
            omit_len:

        Returns:

        """
        if not isinstance(body, (str, bytes)):
            return body

        body_len = len(body)
        if body_len <= omit_len:
            return body

        omitted_body = body[0:omit_len]

        appendix_str = f" ... OMITTED {body_len - omit_len} CHARACTORS ..."
        if isinstance(body, bytes):
            appendix_str = appendix_str.encode("utf-8")

        return omitted_body + appendix_str

    @staticmethod
    def get_raw_md5(data):
        """
        计算md5 md5的输入必须为bytes
        Args:
            data:

        Returns:

        """
        m2 = hashlib.md5(DataHand.to_bytes(data))
        etag = '"' + str(m2.hexdigest()) + '"'
        return etag

    @staticmethod
    def get_md5(data):
        """
        计算 base64 md5 md5的输入必须为bytes
        Args:
            data:

        Returns:

        """
        m2 = hashlib.md5(DataHand.to_bytes(data))
        md5 = base64.standard_b64encode(m2.digest())
        return md5

    @staticmethod
    def get_content_md5(body):
        """
        计算任何输入流的md5值
        Args:
            body:

        Returns:

        """
        if isinstance(body, text_type) or isinstance(body, binary_type):
            return DataHand.get_md5(body)
        elif hasattr(body, 'tell') and hasattr(body, 'seek') and hasattr(body, 'read'):
            file_position = body.tell()  # 记录文件当前位置
            # avoid OOM
            md5 = hashlib.md5()
            chunk = body.read(DEFAULT_CHUNK_SIZE)
            while chunk:
                md5.update(DataHand.to_bytes(chunk))
                chunk = body.read(DEFAULT_CHUNK_SIZE)
            md5_str = base64.standard_b64encode(md5.digest())
            try:
                body.seek(file_position)  # 恢复初始的文件位置
            except Exception as e:
                raise Exception('seek unsupported to calculate md5!')
            return md5_str
        else:
            raise Exception('unsupported body type to calculate md5!')
        return None

    @staticmethod
    def dict_to_xml(data):
        """
        V5使用xml格式，将输入的dict转换为xml
        Args:
            data:

        Returns:

        """
        doc = xml.dom.minidom.Document()
        root = doc.createElement('CompleteMultipartUpload')
        doc.appendChild(root)

        if 'Part' not in data:
            raise Exception("Invalid Parameter, Part Is Required!")

        for i in data['Part']:
            node_part = doc.createElement('Part')

            if 'PartNumber' not in i:
                raise Exception("Invalid Parameter, PartNumber Is Required!")

            node_number = doc.createElement('PartNumber')
            node_number.appendChild(doc.createTextNode(str(i['PartNumber'])))

            if 'ETag' not in i:
                raise Exception("Invalid Parameter, ETag Is Required!")

            node_etag = doc.createElement('ETag')
            node_etag.appendChild(doc.createTextNode(str(i['ETag'])))

            node_part.appendChild(node_number)
            node_part.appendChild(node_etag)
            root.appendChild(node_part)
        return doc.toxml('utf-8')

    @staticmethod
    def xml_to_dict(data, origin_str="", replace_str=""):
        """
        V5使用xml格式，将response中的xml转换为dict
        Args:
            data:
            origin_str:
            replace_str:

        Returns:

        """
        root = xml.etree.ElementTree.fromstring(data)
        xmldict = Xml2Dict(root)
        xmlstr = str(xmldict)
        if origin_str:
            xmlstr = xmlstr.replace(origin_str, replace_str)
        xmldict = eval(xmlstr)
        return xmldict

    @staticmethod
    def get_id_from_xml(data, name):
        """
        解析xml中的特定字段
        Args:
            data:
            name:

        Returns:

        """
        tree = xml.dom.minidom.parseString(data)
        root = tree.documentElement
        result = root.getElementsByTagName(name)
        # use childNodes to get a list, if has no child get itself
        return result[0].childNodes[0].nodeValue

    @staticmethod
    def format_xml(data, root, lst=list(), parent_child=False):
        """
        将dict转换为xml, xml_config是一个bytes
        Args:
            data:
            root:
            lst:
            parent_child:

        Returns:

        """
        if parent_child:
            xml_config = dicttoxml(data, item_func=lambda x: x[:-1], custom_root=root, attr_type=False)
        else:
            xml_config = dicttoxml(data, item_func=lambda x: x, custom_root=root, attr_type=False)
        for i in lst:
            xml_config = xml_config.replace(DataHand.to_bytes(i + i), DataHand.to_bytes(i))
        return xml_config

    @staticmethod
    def format_values(data):
        """
        格式化headers和params中的values为bytes
        Args:
            data:

        Returns:

        """
        for i in data:
            data[i] = DataHand.to_bytes(data[i])
        return data

    @staticmethod
    def is_json(target_data):
        """
        判断目标源是否为json类型
        Args:
            target_data:
        Returns:
        Examples:
            >>> target_data_ = ["1235678",{"key1":"value", "key2":"value"}]
            >>> DataHand.is_json(target_data_)
        """
        if isinstance(target_data, str):
            try:
                json.loads(target_data)
            except ValueError:
                return False
            return True
        else:
            return False

    @staticmethod
    def duplicate(iterable, keep=lambda x: x, key=lambda x: x, reverse=False):
        """
        保序去重
        Args:
            iterable: 去重的同时要对element做的操作
            keep: 使用哪一部分去重
            key: 是否反向去重
            reverse:
        Returns:
        Examples:
            >>> repetition_list = [3, 4, 5, 2, 4, 1]
            # 正序去重
            >>> DataHand.duplicate(repetition_list)
            # 逆序去重
            >>> DataHand.duplicate(repetition_list, reverse=True)
            # 指定规则去重
            >>> repetition_list = [{"a": 3, "b": 4}, {"a":3, "b": 5}]
            >>> DataHand.duplicate(repetition_list, key=lambda x: x["a"])
            # 去重后仅保留部分数据
            >>> DataHand.duplicate(repetition_list, key=lambda x: x["a"], keep=lambda x: x["b"])
        """
        result = list()
        duplicator = list()
        if reverse:
            iterable = reversed(iterable)
        for i in iterable:
            keep_field = keep(i)
            key_words = key(i)
            if key_words not in duplicator:
                result.append(keep_field)
                duplicator.append(key_words)
        return list(reversed(result)) if reverse else result

    @staticmethod
    def chain_all(iter):
        """
        连接多个序列或字典
        Args:
            iter:
        Returns:
        Examples:
            >>> DataHand.chain_all([[1, 2], [1, 2]])
            >>> DataHand.chain_all([{"a": 1}, {"b": 2}])
        """
        iter = list(iter)
        if not iter:
            return []
        if isinstance(iter[0], dict):
            result = {}
            for i in iter:
                result.update(i)
        else:
            result = reduce(lambda x, y: list(x) + list(y), iter)
        return result

    @staticmethod
    def safely_json_loads(json_str, default_type=dict, escape=True):
        """
        返回安全的json类型
        Args:
            json_str: 要被loads的字符串
            default_type: 若load失败希望得到的对象类型
            escape: 是否将单引号变成双引号
        Returns:
        """
        if not json_str:
            return default_type()
        elif escape:
            return json.loads(default_type(json_str))
        else:
            return json.loads(json_str)

    @staticmethod
    def format_html_string(html):
        """
        格式化html, 去掉多余的字符，类，script等。
        Args:
            html:
        Returns:
        """
        trims = [
            (r"\n", ""),
            (r"\t", ""),
            (r"\r", ""),
            (r"  ", ""),
            (r"\u2018", "'"),
            (r"\u2019", "'"),
            (r"\ufeff", ""),
            (r"\u2022", ":"),
            (r"<([a-z][a-z0-9]*)\ [^>]*>", "<\g<1>>"),
            (r"<\s*script[^>]*>[^<]*<\s*/\s*script\s*>", ""),
            (r"</?a.*?>", ""),
        ]
        return reduce(
            lambda string, replacement: re.sub(replacement[0], replacement[1], string),
            trims,
            html,
        )

    @staticmethod
    def data_type_convert(original: [str, dict], target_type: str):
        """
        数据类型转化
        Args:
            original:
            target_type:
        Returns:
        Examples:
            将两个相同长度的列表转换成字典
            >>> original_1 = (["key1","key2"],["value1","value2"])
            >>> DataHand.data_type_convert(original=original_1, target_type="dict")
            将两个不同长度的列表转换成字典
            >>> original_2 = (["key1","key2","key3"],["value1","value2"])
            >>> DataHand.data_type_convert(original=original_2, target_type="dict")
            将dict转化为dict
            >>> original_3 = {"errcode": 401,"errmsg": "[POST]","data": None}
            >>> DataHand.data_type_convert(original=original_3, target_type="dict")
            将json转化为json
            >>> DataHand.data_type_convert(original=json.dumps(original_3), target_type="json")
            将json转化为字典
            >>> DataHand.data_type_convert(original=json.dumps(original_3), target_type="dict")
            将字典列表转换为单个字典
            >>> original_4 = [{"errcode": 401},original_3]
            >>> DataHand.data_type_convert(original=original_4, target_type="dict")
        """
        if isinstance(original, tuple):
            is_equal_bool = True if len(original[0]) == len(original[1]) else False
            if is_equal_bool:
                result = dict(original)
            else:
                result = dict(zip_longest(original[0], original[1]))
        elif isinstance(original, list):
            result = {}
            for index in original:
                result.update(index)
        elif DataHand.is_json(original):
            result = json.loads(original)
        else:
            result = original
        return json.dumps(result) if target_type == "json" else result

    @staticmethod
    def parser(keyword):
        """
        获取后续的字符对应前面出现过的字符的下标
        Args:
            keyword:
        Returns:
        Examples:
            >>> DataHand.parser(keyword="55588ABE")
        """
        vals_mapping = dict()
        indices_mapping = dict()
        for index, i in enumerate(keyword):
            if i in vals_mapping:
                indices_mapping[index] = vals_mapping[i]
            else:
                indices_mapping[index] = None
                vals_mapping[i] = index
        return indices_mapping

    @staticmethod
    def charged(pay_num, money_num):
        """
        计算余额
        Args:
            pay_num:
            money_num:
        Returns:
        Examples:
            >>> DataHand.charged(13, [1, 3, 5])
        """
        if pay_num == 0:
            return 0
        return min(DataHand.get_min(pay_num, money_num)) + 1

    @staticmethod
    def get_min(pay_num, money_num):
        """
        Args:
            pay_num:
            money_num:
        Returns:
        """
        for money in money_num:
            last_num = pay_num - money
            if last_num < 0:
                continue
            try:
                yield DataHand.charged(last_num, money_num)
            except ValueError:
                continue

    @staticmethod
    def dict_to_from(raw_data):
        """
        字典转xwww-from格式
        Args:
            raw_data:

        Returns:
        Examples:
            >>> raw_data_ = {"a": 1, "b":2}
            ... DataHand.dict_to_from(raw_data_)
        """
        if isinstance(raw_data, dict):
            return "&".join(["{}={}".format(key, value) for key, value in raw_data.items()])
        else:
            return raw_data

    @staticmethod
    def form_to_dict(raw_data):
        """
        x-www-from格式转字典
        Args:
            raw_data:

        Returns:
        Examples:
            >>> raw_data_ = "a=1&b=2"
            >>> DataHand.form_to_dict(raw_data_)
        """
        if isinstance(raw_data, str):
            converted_dict = {}
            for k_v in raw_data.split("&"):
                try:
                    key, value = k_v.split("=")
                except ValueError:
                    raise Exception("Invalid x_www_form_urlencoded data format: {}".format(raw_data))
                converted_dict[key] = unquote(value)
            return converted_dict
        else:
            return raw_data


class HtmlHand:
    @staticmethod
    def find(res, xpath, index) -> Text:
        """
        获取html中的数据
        :param res:
        :param xpath:
        :param index:
        :return:
        """
        return etree.HTML(res).xpath(xpath)[index]

    @staticmethod
    def border(sum_str, left_str, right_str, offset=0):
        """
        根据字符串左右边界获取内容
        offset:要获得匹配的第几个数据,默认第一个
        :param sum_str:
        :param left_str:
        :param right_str:
        :param offset:
        :return:
        """
        regex = "([\\s\\S]*?)"
        r = re.compile(left_str + regex + right_str)
        result = r.findall(sum_str)
        if str(offset) == "all":
            return result
        else:
            if len(result) >= offset and len(result) != 0:
                return result[offset]
            else:
                return None


class JsonHand:
    @staticmethod
    def normalize(filter):
        """
        normalize the path expression; outside JsonHand to allow testings
        :param filter: 需要查找的值
        :return:
        """
        subx = []

        # replace index/filter expressions with placeholders
        # Python anonymous functions (lambdas) are cryptic, hard to debug
        def f1(m):
            n = len(subx)  # before append
            g1 = m.group(1)
            subx.append(g1)
            ret = "[#%d]" % n
            # print("f1:", g1, ret)
            return ret

        filter = re.sub(r"[\['](\??\(.*?\))[\]']", f1, filter)
        filter = re.sub(r"'?(?<!@)\.'?|\['?", ";", filter)
        filter = re.sub(r";;;|;;", ";..;", filter)
        filter = re.sub(r";$|'?\]|'$", "", filter)

        # put expressions back
        def f2(m):
            g1 = m.group(1)
            #       print("f2:", g1)
            return subx[int(g1)]

        filter = re.sub(r"#([0-9]+)", f2, filter)
        return filter

    @staticmethod
    def find(obj, expr, result_type="VALUE", debug=0, use_eval=True):
        """
        traverse JSON object using JsonHand expr, returning values or paths
        /	$	跟节点
        .	@	现行节点
        /	. or []	取子节点
        ..	n/a	就是不管位置，选择所有符合条件的条件
        *	*	匹配所有元素节点
        []	[]	迭代器标示(可以在里面做简单的迭代操作，如数组下标，根据内容选值等)
        &#124	[,]	支持迭代器中做多选
        []	?()	支持过滤操作
        n/a	()	支持表达式计算
        ()	n/a	分组，JsonHand不支持
        """

        def s(x, y):
            """concatenate path elements"""
            return str(x) + ";" + str(y)

        def isint(x):
            """check if argument represents a decimal integer"""
            return x.isdigit()

        def as_path(path):
            """convert internal path representation to
            "full bracket notation" for PATH output"""
            p = "$"
            for piece in path.split(";")[1:]:
                # make a guess on how to index
                # XXX need to apply \ quoting on '!!
                if isint(piece):
                    p += "[%s]" % piece
                else:
                    p += "['%s']" % piece
            return p

        def store(path, object):
            if result_type == "VALUE":
                result.append(object)
            elif result_type == "IPATH":  # Index format path (Python ext)
                # return list of list of indices -- can be used w/o "eval" or
                # split
                result.append(path.split(";")[1:])
            else:  # PATH
                result.append(as_path(path))
            return path

        def trace(expr, obj, path):
            if debug:
                print("trace", expr, "/", path)
            if expr:
                x = expr.split(";")
                loc = x[0]
                x = ";".join(x[1:])
                if debug:
                    print("\t", loc, type(obj))
                if loc == "*":

                    def f03(key, loc, expr, obj, path):
                        if debug > 1:
                            print(r"\tf03", key, loc, expr, path)
                        trace(s(key, expr), obj, path)

                    walk(loc, x, obj, path, f03)
                elif loc == "..":
                    trace(x, obj, path)

                    def f04(key, loc, expr, obj, path):
                        if debug > 1:
                            print(r"\tf04", key, loc, expr, path)
                        if isinstance(obj, dict):
                            if key in obj:
                                trace(s("..", expr), obj[key], s(path, key))
                        else:
                            if key < len(obj):
                                trace(s("..", expr), obj[key], s(path, key))

                    walk(loc, x, obj, path, f04)
                elif loc == "!":

                    def f06(key, loc, expr, obj, path):
                        if isinstance(obj, dict):
                            trace(expr, key, path)

                    walk(loc, x, obj, path, f06)
                elif isinstance(obj, dict) and loc in obj:
                    trace(x, obj[loc], s(path, loc))
                elif isinstance(obj, list) and isint(loc):
                    iloc = int(loc)
                    if debug:
                        print("----->", iloc, len(obj))
                    if len(obj) > iloc:
                        trace(x, obj[iloc], s(path, loc))
                else:
                    # [(index_expression)]
                    if loc.startswith("(") and loc.endswith(")"):
                        if debug > 1:
                            print("index", loc)
                        e = evalx(loc, obj)
                        trace(s(e, x), obj, path)
                        return

                    # ?(filter_expression)
                    if loc.startswith("?(") and loc.endswith(")"):
                        if debug > 1:
                            print("filter", loc)

                        def f05(key, loc, expr, obj, path):
                            if debug > 1:
                                print("f05", key, loc, expr, path)
                            if isinstance(obj, dict):
                                eval_result = evalx(loc, obj[key])
                            else:
                                eval_result = evalx(loc, obj[int(key)])
                            if eval_result:
                                trace(s(key, expr), obj, path)

                        loc = loc[2:-1]
                        walk(loc, x, obj, path, f05)
                        return

                    m = re.match(r"(-?[0-9]*):(-?[0-9]*):?(-?[0-9]*)$", loc)
                    if m:
                        if isinstance(obj, (dict, list)):

                            def max(x, y):
                                if x > y:
                                    return x
                                return y

                            def min(x, y):
                                if x < y:
                                    return x
                                return y

                            objlen = len(obj)
                            s0 = m.group(1)
                            s1 = m.group(2)
                            s2 = m.group(3)

                            # XXX int("badstr") raises exception
                            start = int(s0) if s0 else 0
                            end = int(s1) if s1 else objlen
                            step = int(s2) if s2 else 1

                            if start < 0:
                                start = max(0, start + objlen)
                            else:
                                start = min(objlen, start)
                            if end < 0:
                                end = max(0, end + objlen)
                            else:
                                end = min(objlen, end)

                            for i in range(start, end, step):
                                trace(s(i, x), obj, path)
                        return

                    # after (expr) & ?(expr)
                    if loc.find(",") >= 0:
                        # [index,index....]
                        for piece in re.split(r"'?,'?", loc):
                            if debug > 1:
                                print("piece", piece)
                            trace(s(piece, x), obj, path)
            else:
                store(path, obj)

        def walk(loc, expr, obj, path, funct):
            if isinstance(obj, list):
                for i in range(0, len(obj)):
                    funct(i, loc, expr, obj, path)
            elif isinstance(obj, dict):
                for key in obj:
                    funct(key, loc, expr, obj, path)

        def evalx(loc, obj):
            """eval expression"""
            if debug:
                print("evalx", loc)
            # a nod to JavaScript. doesn't work for @.name.name.length
            # Write len(@.name.name) instead!!!
            loc = loc.replace("@.length", "len(__obj)")
            loc = loc.replace("&&", " and ").replace("||", " or ")

            # replace !@.name with 'name' not in obj
            # XXX handle !@.name.name.name....
            def notvar(m):
                return "'%s' not in __obj" % m.group(1)

            loc = re.sub(r"!@\.([a-zA-Z@_0-9-]*)", notvar, loc)

            # replace @.name.... with __obj['name']....
            # handle @.name[.name...].length
            def varmatch(m):
                def brackets(elts):
                    ret = "__obj"
                    for e in elts:
                        if isint(e):
                            ret += "[%s]" % e  # ain't necessarily so
                        else:
                            ret += "['%s']" % e  # XXX beware quotes!!!!
                    return ret

                g1 = m.group(1)
                elts = g1.split(".")
                if elts[-1] == "length":
                    return "len(%s)" % brackets(elts[1:-1])
                return brackets(elts[1:])

            loc = re.sub(r"(?<!\\)(@\.[a-zA-Z@_.0-9]+)", varmatch, loc)
            # removed = -> == translation
            # causes problems if a string contains =
            # replace @  w/ "__obj", but \@ means a literal @
            loc = re.sub(r"(?<!\\)@", "__obj", loc).replace(r"\@", "@")
            if not use_eval:
                if debug:
                    print("eval disabled")
                raise Exception("eval disabled")
            if debug:
                print("eval", loc)
            try:
                # eval w/ caller globals, w/ local "__obj"!
                v = eval(loc, caller_globals, {"__obj": obj})
            except Exception as e:
                if debug:
                    print(repr(e))
                return False

            if debug:
                print("->", v)
            return v

        # body of JsonHand()
        # Get caller globals so eval can pick up user functions!!!
        caller_globals = sys._getframe(1).f_globals
        result = []
        if expr and obj:
            cleaned_expr = JsonHand.normalize(expr)
            if cleaned_expr.startswith("$;"):
                cleaned_expr = cleaned_expr[2:]
            # XXX wrap this in a try??
            trace(cleaned_expr, obj, "$")
            if len(result) > 0:
                return result
        return False


if __name__ == "__main__":
    data = {
        "code": 200,
        "message": "success",
        "data": [
            {
                "year": 2016,
                "months": [
                    {
                        "url": "https://blog.csdn.net/qq_38795430/article/month/2020/07",
                        "count": 1,
                        "month": "07",
                    },
                    {
                        "url": "https://blog.csdn.net/qq_38795430/article/month/2020/03",
                        "count": 2,
                        "month": "03",
                    },
                    {
                        "url": "https://blog.csdn.net/qq_38795430/article/month/2020/01",
                        "count": 1,
                        "month": "01",
                    },
                ],
                "count": 4,
                "currentYear": False,
            },
            {
                "year": 2017,
                "months": [
                    {
                        "url": "https://blog.csdn.net/qq_38795430/article/month/2019/09",
                        "count": 6,
                        "month": "09",
                    },
                    {
                        "url": "https://blog.csdn.net/qq_38795430/article/month/2019/08",
                        "count": 3,
                        "month": "08",
                    },
                    {
                        "url": "https://blog.csdn.net/qq_38795430/article/month/2019/07",
                        "count": 5,
                        "month": "07",
                    },
                    {
                        "url": "https://blog.csdn.net/qq_38795430/article/month/2019/06",
                        "count": 1,
                        "month": "06",
                    },
                ],
                "count": 29,
                "currentYear": False,
            },
            {
                "years": 2018,
                "months": [
                    {
                        "url": "https://blog.csdn.net/qq_38795430/article/month/2018/10",
                        "count": 2,
                        "month": "10",
                    }
                ],
                "count": 2,
                "currentYear": False,
            },
        ],
    }
    # 获取month的所有值
    print("获取month的所有值：" + str(JsonHand.find(data, "$..month")))

    # 获取data下面所有元素
    print("获取data下面所有元素：" + str(JsonHand.find(data, "$.data")))
    print("获取data下面所有元素：" + str(JsonHand.find(data, "$.data.*")))

    # 获取data下面所有year的值
    print("获取data下面所有year的值：" + str(JsonHand.find(data, "$.data[*].year")))
    print("获取data下面所有year的值：" + str(JsonHand.find(data, "$.data..year")))

    # 获取data第1列所有数据
    print("获取data第1列所有数据：" + str(JsonHand.find(data, "$.data[0]")))

    # 获取第2~3列所有数据
    print("获取data第2~3列所有数据：" + str(JsonHand.find(data, "$.data[1:2]")))

    # 获取data最后一列数据
    print("获取data最后一列数据：" + str(JsonHand.find(data, "$.data[(@.length-1)]")))

    # 获取包含了years且条件的数据
    print(
        "获取包含了years且等于2018的数据：" + str(JsonHand.find(data, "$.data[?(@.years==2018)]"))
    )
    print("获取包含了years且≥2018的数据：" + str(JsonHand.find(data, "$.data[?(@.years>=2018)]")))
    print("获取包含了year且<2018的数据：" + str(JsonHand.find(data, "$.data[?(@.year<2017)]")))
    test_str = "获取包含了year且<2018的数"
    print(HtmlHand.border(sum_str=test_str, left_str="获取", right_str="year"))
