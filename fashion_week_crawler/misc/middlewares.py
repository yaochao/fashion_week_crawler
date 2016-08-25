#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/8/11

import random
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class DownloaderMiddleware(object):
    def __init__(self):
        self.useragents = settings.getlist('USER_AGENTS')

    # 每当有request时,会自动调用此方法
    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.useragents))
