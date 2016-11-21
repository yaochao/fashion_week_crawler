#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/11/18
import hashlib


def md5(str):
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()