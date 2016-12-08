#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/12/8

import scrapy
from scrapy import Spider, Request

class WeiboSearchSpider(Spider):
    name = 'weibosearch'
    start_urls = [
        'http://m.weibo.com/page/pageJson?containerid=&containerid=100103type%3D1%26q%3D周杰伦&type=all&queryVal=周杰伦&title=周杰伦&v_p=11&ext=&fid=100103type%3D1%26q%3D周杰伦&uicode=10000011&next_cursor=&page=2'
    ]
    custom_settings = {

    }

    def start_requests(self):
        request = Request(url=self.start_urls[0], callback=self.parse)
        yield request

    def parse(self, response):
        print response.content
        print response.headers
        print response