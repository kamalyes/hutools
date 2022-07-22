# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  mail.py
@Time    :  2022/6/17 12:55 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr


class MailManger:
    def __init__(self, host, port, sender, password, nickname=None):
        self.host = host
        self.port = int(port)
        self.user = sender
        self.password = password
        self.nickname = nickname

    def get_server(self):
        if self.port == 465:
            server = smtplib.SMTP_SSL(self.host, self.port)
        elif self.port == 587:
            server = smtplib.SMTP(self.host, self.port)
            server.ehlo()
            server.starttls()
        else:
            server = smtplib.SMTP(self.host, self.port)
        server.login(self.user, self.password)
        return server

    def send_text_mail(self, receivers, subject, body):
        server = self.get_server()
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = formataddr((self.nickname, self.user)) if self.nickname else self.user
        server.sendmail(self.user, receivers, msg.as_string())
        server.quit()
