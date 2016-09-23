#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/9/23
import json
from bs4 import BeautifulSoup
import time
from scrapy import Spider, Request

from fashion_week_crawler.items import WeiboItem


class WeiboSpider(Spider):
    name = 'weibo'
    start_urls = [
        'http://m.weibo.cn/page/json?containerid=1005051655526104_-_WEIBO_SECOND_PROFILE_WEIBO&page=1',
        'http://m.weibo.cn/page/json?containerid=1005051667999147_-_WEIBO_SECOND_PROFILE_WEIBO&page=1',
        'http://m.weibo.cn/page/json?containerid=1005051656851485_-_WEIBO_SECOND_PROFILE_WEIBO&page=1',
        'http://m.weibo.cn/page/json?containerid=1005052499342795_-_WEIBO_SECOND_PROFILE_WEIBO&page=1',
        'http://m.weibo.cn/page/json?containerid=1005052547393100_-_WEIBO_SECOND_PROFILE_WEIBO&page=1',
        'http://m.weibo.cn/page/json?containerid=1005051654502821_-_WEIBO_SECOND_PROFILE_WEIBO&page=1',
        'http://m.weibo.cn/page/json?containerid=1005051644112857_-_WEIBO_SECOND_PROFILE_WEIBO&page=1'
    ]
    custom_settings = {
        'FEED_URI': '/Users/yaochao/Desktop/weibo.csv',
        'FEED_FORMAT': 'CSV',
        'ITEM_PIPELINES': {
            'fashion_week_crawler.pipelines.WeiboPipeline': 100,
        },
    }

    def parse(self, response):
        dict = json.loads(s=response.body)
        url_prefix = response.url.split('&page=')[0] + '&page='
        page_total = dict['count'] / 10.0 if dict['count'] / 10.0 == 0.0 else dict['count'] / 10 + 1
        for page in xrange(page_total):
            url = url_prefix + str(page + 1)
            request = Request(url=url, callback=self.parse_content)
            yield request

    def parse_content(self, response):
        item = WeiboItem()
        dict = json.loads(s=response.body)
        card_group = dict['cards'][0]['card_group']
        for card in card_group:
            mblog = card['mblog']
            text = mblog['text']
            soup = BeautifulSoup(text)
            text = ''
            for string in soup.strings:
                text = text + string
            item['text'] = text
            timestamp = mblog['created_timestamp']
            t = time.localtime(float(timestamp))
            t = time.strftime('%Y年%m月%d日 %H:%M:%S', t)
            item['time'] = t
            print item
            yield item
