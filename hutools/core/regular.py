# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  regex.py
@Time    :  2021/10/22 20:16
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  正则匹配
"""

import re
from typing import Any

from hutools.cron import BatchTask


class RegEx:

    @staticmethod
    def match_email(context: Any) -> bool:
        """
        效验邮箱格式
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ["test@163.com","test163.com","155555@qq.com"]
            >>> BatchTask.list_jobs(RegEx.match_email, examples)
        """
        return (
            True
            if re.match(
                "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)",
                str(context),
            )
            else False
        )

    @staticmethod
    def date_validator(value: str) -> bool:
        """
        # 判断是否是日期字符串
        """
        value = value.strip()
        try:
            if len(value) == 10:
                datetime.strptime(value, '%Y-%m-%d')
                return True
            elif len(value) == 19:
                datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                return True
        except ValueError:
            pass
        return False

    @staticmethod
    def match_double_byte_str(context: Any) -> bool:
        """
        效验是否存在双字节
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ["哈哈哈", "12356", "abc", "ABC" "QS12356", "QS12356哈哈哈"]
            >>> BatchTask.list_jobs(RegEx.match_double_byte_str, examples)
        """
        return True if re.match(r".*?([^x00-xff])", str(context)) else False

    @staticmethod
    def weak_pwd(context: Any) -> bool:
        """
        效验密码是否为弱密码 (最低要求数字、英文、符合各一个、长度限制：7~20)
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ["哈哈哈", "12356", "abc", "ABC" "QS12356", "QS12356哈哈哈", None, "QSa12356@"]
            >>> BatchTask.list_jobs(RegEx.weak_pwd, examples)
        """
        return (
            True
            if re.match(
                r"^(?:(?=.*[0-9].*)(?=.*[A-Za-z].*)(?=.*[\W].*))[\W0-9A-Za-z]{7,20}",
                str(context),
            )
               is None
            else False
        )

    @staticmethod
    def match_mobile(context: Any) -> bool:
        """
        效验手机号格式
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ["哈哈哈", "12356", "abc", "ABC" "QS12356", "QS12356哈哈哈", None, "QSa12356@",
            ... "+8617888829981","008618311006933","19119255552"]
            >>> BatchTask.list_jobs(RegEx.match_mobile, examples)
        """
        rule = "^(?:(?:\\+|00)86)?1(?:(?:3[\\d])|(?:4[5-79])|" \
               "(?:5[0-35-9])|(?:6[5-7])|(?:7[0-8])|(?:8[\\d])|(?:9[189]))\\d{8}"
        return True if re.match(rule, str(context)) else False

    @staticmethod
    def match_ipv4(context: Any) -> bool:
        """
        效验ipv4格式
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ["哈哈哈", "12356", "abc", "ABC" "QS12356", "QS12356哈哈哈", None,
            ... "QSa12356@", "+8617888829981","008618311006933","19119255552", "127.16.0.0"]
            >>> BatchTask.list_jobs(RegEx.match_ipv4, examples)
        """
        rule = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return True if re.match(rule, str(context)) else False

    @staticmethod
    def match_str_length(context: Any, min_length=15, max_length=17) -> bool:
        """
        效验数字长度是否在区间值内
        Args:
            context:
            min_length:
            max_length:
        Returns:
        Examples:
            >>> examples = [17, 12355678901235567, "哈哈哈", "12356", "abc", "ABC" "QS12356", "QS12356哈哈哈", None,
            ... "QSa12356@", "+8617888829981","008618311006933","19119255552", "127.16.0.0"]
            >>> BatchTask.list_jobs(RegEx.match_str_length, examples)
        """
        rule = "^\\d{%s,%s}" % (min_length, max_length)
        return True if re.match(rule, str(context)) else False

    @staticmethod
    def match_username(context, min_length=7, max_length=20):
        """
        效验用户名格式 (必须由英文开头、长度限制：7~20)
        Args:
            context:
            min_length:
            max_length:
        Returns:
        Examples:
            >>> examples = [17, 12355678901235567, "QS356", "哈哈哈", "12356", "abc", "ABC" "QS12356", "QS12356哈哈哈", None,
            ... "QSa12356@", "+8617888829981","008618311006933","19119255552", "127.16.0.0"]
            >>> BatchTask.list_jobs(RegEx.match_username, examples)
        """
        rule = r"^(?=.*[A-Za-z])[a-zA-Z0-9]{%s,%s}" % (min_length, max_length)
        return True if re.match(rule, str(context)) else False

    @staticmethod
    def match_valid_url(context):
        """
        效验url
        context:
        Returns:
        Examples:
            >>> examples = ["https://www.baidu.com", "127.0.0.1:8000", "https://www.sweets.cn:8080", "127.16.0.0",
            ... 17, 12355678901235567, "QS356", "哈哈哈", "12356", "abc", "ABC" "QS12356", "QS12356哈哈哈", None,
            ... "QSa12356@", "+8617888829981","008618311006933","19119255552"]
            >>> BatchTask.list_jobs(RegEx.match_valid_url, examples)
        """
        rule = r"^(((ht|f)tps?):\/\/)?[\w-]+(\.[\w-]+)+([\w.@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?$"
        return True if re.match(rule, str(context)) else False

    @staticmethod
    def match_trail_type(context, method=None):
        """
        效验尾缀格式
        Args:
            context:
            method:
        Returns:
        Examples:
            >>> examples = [".bat", ".image", ".png", "image"]
            >>> BatchTask.list_jobs(RegEx.match_trail_type, examples)
        """
        image = ".*(\.png|\.jpg|\.jpeg|\.gif|\.mov)$"
        video = ".*(\.mp4|\.avi|\.mkv|\.flv|\.vob)$"
        exe = ".*(\.exe|\.sh|\.bat)$"
        docs = ".*(\.md|\.xls|\.xlsx|\.word|\.pdf)$"
        if method == "image":
            rule = image
        elif method == "video":
            rule = video
        elif method == "docs":
            rule = docs
        else:
            rule = exe
        return True if re.match(rule, str(context).lower()) else False

    @staticmethod
    def match_train_number(context: Any) -> bool:
        """
         火车车次
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_train_number('G1868')
            >>> examples = ['G1868', 'D102', 'D9', 'Z5', 'Z26', 'Z17']
            >>> BatchTask.list_jobs(RegEx.match_train_number, examples)
        """
        return (
            True
            if re.match(
                "^[GCDZTSPKXLY1-9]\d{1,4}$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_phone_imei(context: Any) -> bool:
        """
         手机机身码(IMEI)
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_phone_imei('1235567890')
            >>> RegEx.match_phone_imei('123556789012355')
            >>> examples = ['123556789012355', '1235567890123556', '12355678901235567']
            >>> BatchTask.list_jobs(RegEx.match_phone_imei, examples)
        """
        return (
            True
            if re.match(
                "^\d{15,17}$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_ip(context: Any) -> bool:
        """
         必须带端口号的网址(或ip)
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_ip('127.0.0.1:5050')
            >>> RegEx.match_ip('https://www.123.com')
            >>> RegEx.match_ip('https://www.123.com:8080')
            >>> examples = ['https://www.qq.com:8080', '127.0.0.1:5050', 'baidu.com:8001', 'http://192.168.1.1:9090']
            >>> BatchTask.list_jobs(RegEx.match_ip, examples)
        """
        return (
            True
            if re.match(
                "^((ht|f)tps?:\/\/)?[\w-]+(\.[\w-]+)+:\d{1,5}\/?$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_url(context: Any) -> bool:
        """
         网址(URL)
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_url('www.123.com')
            >>> RegEx.match_url('https://vuejs.org/v2/api/#v-model')
            >>> RegEx.match_url('//www.123.com')
            >>> examples = ['ftp://baidu.123', 'https://www.amap.com/search?id=BV10060895&city=420111']
            >>> BatchTask.list_jobs(RegEx.match_url, examples)
        """
        return (
            True
            if re.match(
                "^(((ht|f)tps?):\/\/)?([^!@#$%^&*?.\s-]([^!@#$%^&*?.\s]{0,63}[^!@#$%^&*?.\s])?\.)+[a-z]{2,6}\/?",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_social_credit(context: Any) -> bool:
        """
         统一社会信用代码
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_social_credit('9111010')
            >>> RegEx.match_social_credit('92371000MA3MXH0E3W')
            >>> examples = ['91230186MA1B7FLT55', '92371000MA3MXH0E3W']
            >>> BatchTask.list_jobs(RegEx.match_social_credit, examples)
        """
        return (
            True
            if re.match(
                "^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_easy_social_credit(context: Any) -> bool:
        """
         统一社会信用代码(宽松匹配)(15位/18位/20位数字/字母)
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_easy_social_credit('91110108772551611J')
            >>> examples = ['91110108772551611J', '911101085923662400']
            >>> BatchTask.list_jobs(RegEx.match_easy_social_credit, examples)
        """
        return (
            True
            if re.match(
                "^(([0-9A-Za-z]{15})|([0-9A-Za-z]{18})|([0-9A-Za-z]{20}))$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_net_mask(context: Any) -> bool:
        """
         子网掩码(不包含 0.0.0.0)
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_net_mask('2')
            >>> RegEx.match_net_mask('255.255.255.0')
            >>> examples = ['255.255.255.0', '255.255.255.255', '255.240.0.0']
            >>> BatchTask.list_jobs(RegEx.match_net_mask, examples)
        """
        return (
            True
            if re.match(
                "^(254|252|248|240|224|192|128)\.0\.0\.0|255\.(254|252|248|240|224|192|128|0)\.0\.0|255\.255\.(254|252|248|240|224|192|128|0)\.0|255\.255\.255\.(255|254|252|248|240|224|192|128|0)$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_md5_format(context: Any) -> bool:
        """
         md5格式(32位)
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_md5_format('21fe181c5bfc16306a6828c1f7b762e8')
            >>> examples = ['21fe181c5bfc','21fe181c5bfc16306a6828c1f7b762e8']
            >>> BatchTask.list_jobs(RegEx.match_md5_format, examples)
        """
        return (
            True
            if re.match(
                "^([a-f\d]{32}|[A-F\d]{32})$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_uuid_format(context: Any) -> bool:
        """
         GUID/UUID
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_uuid_format('51E3DAF5-6E37-4BCC-9F8E-0D9521E2AA8D')
            >>> examples = ['21fe181c5bfc','21fe181c5bfc16306a6828c1f7b762e8','51E3DAF5-6E37-4BCC-9F8E-0D9521E2AA8D']
            >>> BatchTask.list_jobs(RegEx.match_uuid_format, examples)
        """
        return (
            True
            if re.match(
                "^[a-f\d]{4}(?:[a-f\d]{4}-){4}[a-f\d]{12}$/i",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_version_format(context: Any) -> bool:
        """
         版本号(version)格式必须为X.Y.Z
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_version_format('16.5')
            >>> RegEx.match_version_format('16.5.16')
        """
        return (
            True
            if re.match(
                "^\d+(?:\.\d+){2}$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_image_url_format(context: Any) -> bool:
        """
         图片(image)链接地址（图片格式可按需增删）
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ['www.123.com/logo.png', 'https://www.abc.com/logo.png']
            >>> BatchTask.list_jobs(RegEx.match_image_url_format, examples)
        """
        return (
            True
            if re.match(
                "^https?:\/\/(.+\/)+.+(\.(gif|png|jpg|jpeg|webp|svg|psd|bmp|tif))$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_video_url_format(context: Any) -> bool:
        """
         视频(video)链接地址（视频格式可按需增删）
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ['www.123.com/lwc.avi', 'https://www.abc.com/logo.mpg']
            >>> BatchTask.list_jobs(RegEx.match_video_url_format, examples)
        """
        return (
            True
            if re.match(
                "^https?:\/\/(.+\/)+.+(\.(swf|avi|flv|mpg|rm|mov|wav|asf|3gp|mkv|rmvb|mp4))$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_24hms_time_format(context: Any) -> bool:
        """
         24小时制时间（HH:mm:ss）
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_24hms_time_format('23:35:55')
        """
        return (
            True
            if re.match(
                "^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_12hms_time_format(context: Any) -> bool:
        """
         12小时制时间（HH:mm:ss）
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_12hms_time_format('01:00:00')
            >>> RegEx.match_12hms_time_format('12:00:00')
            >>> RegEx.match_12hms_time_format('23:35:55')
        """
        return (
            True
            if re.match(
                "^(?:1[0-2]|0?[1-9]):[0-5]\d:[0-5]\d$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_base64_format(context: Any) -> bool:
        """
         base64格式
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_base64_format('data:image/gif;base64,xxxx==')
        """
        return (
            True
            if re.match(
                "^\s*data:(?:[a-z]+\/[a-z0-9-+.]+(?:;[a-z-]+=[a-z0-9-]+)?)?(?:;base64)?,([a-z0-9!$&',()*+;=\-._~:@/?%\s]*?)\s*$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_easy_currency_format(context: Any) -> bool:
        """
         数字/货币金额（支持负数、千分位分隔符）
        Args:
            context:
        Returns:
        Examples:
            >>> examples = [100, -0.99, 3, 234.32, -1, 900, 235.09, '12,345,678.90']
            >>> BatchTask.list_jobs(RegEx.match_easy_currency_format, examples)
        """
        return (
            True
            if re.match(
                "^-?\d+(,\d{3})*(\.\d{1,2})?$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_chinese_name(context: Any) -> bool:
        """
         中文姓名
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ['葛二蛋', '凯文·杜兰特', '德克·维尔纳·诺维茨基']
            >>> BatchTask.list_jobs(RegEx.match_chinese_name, examples)
        """
        return (
            True
            if re.match(
                "^(?:[\u4e00-\u9fa5·]{2,16})$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_english_name(context: Any) -> bool:
        """
         英文姓名
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ['James', 'Kevin Wayne Durant', 'Dirk Nowitzki']
            >>> BatchTask.list_jobs(RegEx.match_english_name, examples)
        """
        return (
            True
            if re.match(
                "(^[a-zA-Z][a-zA-Z\s]{0,20}[a-zA-Z]$)",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_only_chinese(context: Any) -> bool:
        """
         只有中文/汉字
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ["QS12356","哈哈哈","155555@qq.com","english"]
            >>> BatchTask.list_jobs(RegEx.match_only_chinese, examples)
        """
        return (
            True
            if re.match(
                # "^[\u4E00-\u9FA5]+$",
                "^(?:[\u3400-\u4DB5\u4E00-\u9FEA\uFA0E\uFA0F\uFA11\uFA13\uFA14\uFA1F\uFA21\uFA23\uFA24\uFA27-\uFA29]|"
                "[\uD840-\uD868\uD86A-\uD86C\uD86F-\uD872\uD874-\uD879][\uDC00-\uDFFF]|"
                "\uD869[\uDC00-\uDED6\uDF00-\uDFFF]|\uD86D[\uDC00-\uDF34\uDF40-\uDFFF]|"
                "\uD86E[\uDC00-\uDC1D\uDC20-\uDFFF]|\uD873[\uDC00-\uDEA1\uDEB0-\uDFFF]|"
                "\uD87A[\uDC00-\uDFE0])+$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_only_english(context: Any) -> bool:
        """
         英文字母
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ["https://www.baidu.com", "127.0.0.1:8000", "https://www.sweets.cn:8080", "127.16.0.0",
            ... 17, 12355678901235567, "QS356", "哈哈哈", "12356", "abc", "ABC" "QS12356", "QS12356哈哈哈", None,
            ... "QSa12356@", "+8617888829981","008618311006933","19119255552"]
            >>> BatchTask.list_jobs(RegEx.match_only_english, examples)
        """
        return (
            True
            if re.match(
                "^[a-zA-Z]+$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_only_decimals(context: Any) -> bool:
        """
         小数
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ['0.0', '0.09']
            >>> BatchTask.list_jobs(RegEx.match_only_decimals, examples)
        """
        return (
            True
            if re.match(
                "^\d+\.\d+$/",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_only_number(context: Any) -> bool:
        """
         只包含数字
        Args:
            context:
        Returns:
        Examples:
            >>> RegEx.match_only_number(1235678)
            >>> RegEx.match_only_number('1235678')
            >>> RegEx.match_only_number('class')
            >>> RegEx.match_only_number('啊啊呸啊呸')
        """
        return (
            True
            if re.match(
                "^\d+$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_only_number_and_letters(context: Any) -> bool:
        """
         数字和字母组成
        Args:
            context:
        Returns:
        Examples:
            >>> examples =  ['james666', '125666', '啊呸']
            >>> BatchTask.list_jobs(RegEx.match_only_number_and_letters, examples)
        """
        return (
            True
            if re.match(
                "^[A-Za-z0-9]+$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_only_lowe_letters(context: Any) -> bool:
        """
         小写英文字母组成
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ['russel', 'ABC', '1235678', 'Ab123']
            >>> BatchTask.list_jobs(RegEx.match_only_lowe_letters, examples)
        """
        return (
            True
            if re.match(
                "^[a-z]+$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_only_upper_letters(context: Any) -> bool:
        """
         大写英文字母
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ['russel', 'ABC', '1235678', 'Ab123']
            >>> BatchTask.list_jobs(RegEx.match_only_upper_letters, examples)
        """
        return (
            True
            if re.match(
                "^[A-Z]+$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_only_chinese_and_number(context: Any) -> bool:
        """
         中文和数字
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ['哈哈哈', '你好6777啊', 'abc', 'ABC', '1235678', '@¥()！']
            >>> BatchTask.list_jobs(RegEx.match_only_chinese_and_number, examples)
        """
        return (
            True
            if re.match(
                "^((?:[\u3400-\u4DB5\u4E00-\u9FEA\uFA0E\uFA0F\uFA11\uFA13\uFA14\uFA1F\uFA21\uFA23\uFA24\uFA27-\uFA29]|"
                "[\uD840-\uD868\uD86A-\uD86C\uD86F-\uD872\uD874-\uD879][\uDC00-\uDFFF]|"
                "\uD869[\uDC00-\uDED6\uDF00-\uDFFF]|\uD86D[\uDC00-\uDF34\uDF40-\uDFFF]|"
                "\uD86E[\uDC00-\uDC1D\uDC20-\uDFFF]|\uD873[\uDC00-\uDEA1\uDEB0-\uDFFF]|"
                "\uD87A[\uDC00-\uDFE0])|(\d))+$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_not_exists_letters(context: Any) -> bool:
        """
         不能包含字母
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ['哈哈哈', '你好6啊', 'abc', 'ABC', '1235678', '@¥()！']
            >>> BatchTask.list_jobs(RegEx.match_not_exists_letters, examples)
        """
        return (
            True
            if re.match(
                "^((?:[\u3400-\u4DB5\u4E00-\u9FEA\uFA0E\uFA0F\uFA11\uFA13\uFA14\uFA1F\uFA21\uFA23\uFA24\uFA27-\uFA29]|"
                "[\uD840-\uD868\uD86A-\uD86C\uD86F-\uD872\uD874-\uD879][\uDC00-\uDFFF]|"
                "\uD869[\uDC00-\uDED6\uDF00-\uDFFF]|\uD86D[\uDC00-\uDF34\uDF40-\uDFFF]|"
                "\uD86E[\uDC00-\uDC1D\uDC20-\uDFFF]|\uD873[\uDC00-\uDEA1\uDEB0-\uDFFF]|"
                "\uD87A[\uDC00-\uDFE0])|(\d))+$",
                str(context),
            )
            else False
        )

    @staticmethod
    def match_ascii_special_char(context: Any) -> bool:
        """
         ASCII码表中的全部的特殊字符
        Args:
            context:
        Returns:
        Examples:
            >>> examples = ["[", ".", "^", "&3%", "1235678", "abc", "ABC", "ABCa123"]
            >>> BatchTask.list_jobs(RegEx.match_ascii_special_char, examples)
        """
        return (
            True
            if re.match(
                "[\x21-\x2F\x3A-\x40\x5B-\x60\x7B-\x7E]+",
                str(context),
            )
            else False
        )
