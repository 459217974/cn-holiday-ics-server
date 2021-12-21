#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
# Created by CaoDa on 2021/12/21 10:11

import hmac
import base64
import struct
import hashlib
import time
import random
import qrcode
import urllib.parse


class GoogleAuth(object):
    s = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    uri_format = 'otpauth://totp/{}?secret={}'

    @classmethod
    def __get_token(cls, secret, intervals_no):
        key = base64.b32decode(secret, True)
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
        return h

    @classmethod
    def get_current_token(cls, secret):
        if isinstance(secret, str):
            secret = secret.encode()
        return cls.__get_token(secret, intervals_no=int(time.time()) // 30)

    @classmethod
    def verify(cls, secret, token):
        return str(cls.get_current_token(secret)) == str(token)

    @classmethod
    def new_secret(cls):
        secret = base64.b32encode(''.join(random.sample(cls.s, 10)).encode())
        return secret.decode()

    @classmethod
    def get_qrcode(cls, secret, account):
        uri = cls.uri_format.format(urllib.parse.quote(account), secret)
        img = qrcode.make(uri)
        return img
