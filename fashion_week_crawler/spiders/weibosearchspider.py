#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/12/8
import copy
import json
import math
import re

from bs4 import BeautifulSoup
from scrapy import Spider, Request


class WeiboSearchSpider(Spider):
    name = 'weibosearch'
    start_urls = []
    keywords = ['比亚迪S7', '瑞风S7', '长安CS95', '传祺GS8', '力帆X80', '东南DX9', '哈弗h6', '传祺gs4', '荣威RX5', '昂科威']
    # keywords = ['比亚迪S7']
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'fashion_week_crawler.pipelines.WeiboSearchKafkaPipeline': 100,
            'fashion_week_crawler.pipelines.WeiboSearchMongodbPipeline': 200,
        }
    }
    headers1 = {
        "Host": "m.weibo.cn",
    }
    headers2 = {
        "Host": "weibo.cn",
        "Referer": "http://weibo.cn/",
    }

    cookies = {
        "_T_WM": "717fc96aca537a169c6b8564941a7040",
        "WEIBOCN_WM": "3349",
        "H5_wentry": "H5",
        "backURL": "http%3A%2F%2Fm.weibo.cn%2F",
        "M_WEIBOCN_PARAMS": "luicode%3D10000011%26lfid%3D100103type%253D1%2526q%253D%25E5%2591%25A8%25E6%259D%25B0%25E4%25BC%25A6",
        "SUB": "_2A251XlweDeRxGeNK41MT8ibLzDqIHXVWoWRWrDV6PUJbktBeLVjmkW1QQa_Y-VF8kP38ZAHADnCmj75Xvw..",
        "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WWuMKPHOA2X.q1EUH8SEIA35NHD95QfShnpeozRS0McWs4Dqcjz9J80U8vQUg2t",
        "SUHB": "0auwqxzsssxhpR",
        "SSOLoginState": "1482304591",
        "ALF": "1484896591",
    }

    def start_requests(self):
        for keyword in self.keywords:
            url = 'http://m.weibo.cn/container/getIndex?containerid=&containerid=100103type%3D1%26q%3D' + keyword + '&type=all&queryVal=' + keyword + '&title=' + keyword + '&v_p=11&ext=&fid=100103type%3D1%26q%3D' + keyword + '&uicode=10000011&next_cursor=&page='
            url = url + '2'
            request = Request(url=url, callback=self.parse)
            request.meta['keyword'] = keyword
            yield request

    def parse(self, response):
        keyword = response.meta['keyword']
        result = json.loads(response.text)
        if result['ok']:
            if result['cards']:
                card_group = result['cards'][0]['card_group']
                for index, card in enumerate(card_group):
                    if card.has_key('mblog'):
                        mblog = card['mblog']
                        _id = mblog['id']
                        text = mblog['text']
                        soup = BeautifulSoup(text, "lxml")
                        text = ''
                        for string in soup.strings:
                            text = text + string
                        source = mblog['source']
                        created_at = mblog['created_at']
                        user = mblog['user']
                        user_id = user['id']
                        user_name = user['screen_name']
                        user_header = user['profile_image_url']
                        user_description = user['description']
                        user_verified = user['verified']
                        user_verify_type = user['verified_type']
                        user_gender = user['gender']
                        followers_count = user['followers_count']
                        item = {
                            '_id': _id,
                            'text': text,
                            'created_at': created_at,
                            'source': source,
                            'user_id': user_id,
                            'user_name': user_name,
                            'user_header': user_header,
                            'user_description': user_description,
                            'user_verified': user_verified,
                            'user_verify_type': user_verify_type,
                            'user_gender': user_gender,
                            'followers_count': followers_count,
                            'keyword': keyword
                        }
                        request = Request(url='http://weibo.cn/' + str(user_id) + '/info',
                                          callback=self.parse_person_home, cookies=self.cookies)
                        request.meta['item'] = copy.deepcopy(item)
                        yield request

        # 下一页
        total_page = result['cardlistInfo']['total'] / 10.0
        total_page = int(math.ceil(total_page))
        maxPage = total_page if total_page < 101 else 101
        for i in range(3, maxPage + 1):
            url = response.url
            url = url.split('&page=')[0]
            next_url = url + '&page=' + str(i)
            request = Request(url=next_url, callback=self.parse)
            request.meta['keyword'] = keyword
            yield request

    def parse_person_home(self, response):
        item = response.meta['item']
        body = response.body
        address_re = r'<br/>地区:(.*?)<br/>'
        address = re.findall(address_re, body)
        address = address[0] if address else None
        item['address'] = address
        yield item
