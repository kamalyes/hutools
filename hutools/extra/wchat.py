# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  ssh.py
@Time    :  2022/6/17 12:55 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  企业微信机器人
"""
import base64
import hashlib
import json
from pathlib import Path

import requests


class FileUploadError(Exception):
    pass


class WeChatChatbot:
    def __init__(self, robot_key):
        self.key = robot_key
        self.url = "https://qyapi.weixin.qq.com/cgi-bin/webhook"
        self.webhook_address = f'{self.url}/cgi-bin/webhook/send?key=' + self.key

    def do_request(self, data):
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        resp = requests.post(self.webhook_address, headers=headers, data=json.dumps(data))
        return resp.json()

    @staticmethod
    def do_image(image_path):
        support_url_prefix = ('http://', 'https://', 'ftp://')
        remote = False

        for i in support_url_prefix:
            if image_path.startswith(i):
                remote = True
                break

        if remote:
            r = requests.get(image_path)
            if r.ok:
                b64_value = base64.b64encode(r.content).decode('utf-8')
                md5_value = hashlib.md5(r.content).hexdigest()
                return b64_value, md5_value
            else:
                return None, None
        else:
            with open(image_path, 'rb') as f:
                content = f.read()
                b64_value = base64.b64encode(content).decode('utf-8')
                md5_value = hashlib.md5(content).hexdigest()
                return b64_value, md5_value

    def send_text(self, content, at_mobiles=None):
        at_mobiles_list = []
        if at_mobiles:
            if isinstance(at_mobiles, str):
                at_mobiles = at_mobiles.split(',')

            at_mobiles = list(at_mobiles)
        else:
            at_mobiles = []

        for member in at_mobiles:
            if member.lower() == 'all':
                at_mobiles_list.append('@all')
            else:
                at_mobiles_list.append(member)

        data = {
            'msgtype': 'text',
            'text': {
                'content': content,
                'mentioned_mobile_list': at_mobiles_list
            }
        }

        return self.do_request(data)

    def send_markdown(self, contents):
        if isinstance(contents, (list, tuple)):
            if len(contents) >= 1:
                send_contents = contents[0] + '\n'
                for content in contents[1:]:
                    send_contents += content + '\n'
            else:
                send_contents = contents[0]
        else:
            send_contents = contents

        data = {
            'msgtype': 'markdown',
            'markdown': {
                'content': send_contents
            }
        }
        return self.do_request(data)

    def send_image(self, image_path):
        image_base64, image_md5 = self.do_image(image_path)
        data = {
            'msgtype': 'image',
            'image': {
                'base64': image_base64,
                'md5': image_md5
            }
        }
        return self.do_request(data)

    def send_news(self, news_title, jump_url, picurl=None, news_description=None):
        data = {
            'msgtype': 'news',
            'news': {
                'articles': [
                    {
                        'title': news_title,
                        'url': jump_url,
                        'description': news_description,
                        'picurl': picurl
                    }
                ]
            }
        }

        return self.do_request(data)

    def put_file(self, file_path):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f'the files <{file_path}> not found')

        put_file_address = f'{self.url}/upload_media?key={self.key}&type=files'

        resp = requests.post(put_file_address,
                             files=[('media', (path.name, open(file_path, 'rb'), 'application/octet-stream'))])
        return resp.json()

    def send_file(self, file_path):
        resp = self.put_file(file_path)
        if resp['errcode'] == 0:
            media_id = resp['media_id']
        else:
            raise FileUploadError(resp)
        data = {
            'msgtype': 'files',
            'files': {
                'media_id': media_id
            }
        }

        return self.do_request(data)
