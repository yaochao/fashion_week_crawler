#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/9/13
import re

from scrapy import Spider, Request
import urllib
from fashion_week_crawler.items import LadyMaxItem


class LadyMaxSpider(Spider):
    name = 'ladymax'
    start_urls = [
        'http://www.ladymax.cn/tag/%E5%B7%B4%E9%BB%8E%E6%97%B6%E8%A3%85%E5%91%A8',
        'http://www.ladymax.cn/tag/%E7%B1%B3%E5%85%B0%E6%97%B6%E8%A3%85%E5%91%A8',
        'http://www.ladymax.cn/tag/%E7%BA%BD%E7%BA%A6%E6%97%B6%E8%A3%85%E5%91%A8',
        'http://www.ladymax.cn/tag/%E4%BC%A6%E6%95%A6%E6%97%B6%E8%A3%85%E5%91%A8'
    ]

    def parse(self, response):

        # 提取标题,二级链接
        a_list = response.xpath('//*[@class="tt"]')
        for a in a_list:
            item = LadyMaxItem()
            title = a.xpath('text()').extract_first()
            page_url = a.xpath('@href').extract_first()
            # print title, page_url
            # item['index_url'] = response.url
            # item['fashionshow_url'] = page_url
            # item['fashionshow_name'] = title
            # request = Request(url=page_url, callback=self.parse_page)
            # request.meta['item'] = item
            # yield request

        # 下一页
        next_re = r"<a href='(.*?)'>下一页</a>".decode('utf-8')
        next_url = re.findall(next_re, response.text)
        if next_url:
            next_url = next_url[0].encode('utf-8')
            next_url = urllib.quote(next_url, safe='/:')
            request = Request(url=next_url, callback=self.parse)
            print next_url
            yield request

    def parse_page(self, response):
        item = response.meta['item']
