#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/9/26

import json
import logging
import re
import time

from scrapy import Request
from scrapy import Spider

from fashion_week_crawler.items import WeixinItem

logger = logging.getLogger(__name__)


class WeixinSpider(Spider):
    name = 'weixin'
    start_urls = [
        'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MzAxODI5NzEyMA==&uin=MTc1Njk1MzE1&key=79512945a1fcb0e25918d33abd587ce29785d7510f0831e5eb8aa9f70fd83203a4c3f17eafed78a01c2f2fdab939e9a4f9ef629c0c3b1bf3&f=json&frommsgid=10000000101&count=10&uin=MTc1Njk1MzE1&key=79512945a1fcb0e25918d33abd587ce29785d7510f0831e5eb8aa9f70fd83203a4c3f17eafed78a01c2f2fdab939e9a4f9ef629c0c3b1bf3&pass_ticket=UfVEX4Ir7gGYuVrVlyYNTIH2eFe2wHa7wNlZrU7%25252FFos%25253D&wxtoken=&x5=1'
    ]

    custom_settings = {
        'FEED_URI': '/Users/yaochao/Desktop/bof_weixin.csv',
        'FEED_FORMAT': 'CSV',
        'ITEM_PIPELINES': {
            'fashion_week_crawler.pipelines.WeiboPipeline': 100,
        },
        'DOWNLOAD_DELAY': 0,
    }

    cookies = {
        "sd_userid": "41481474344172593",
        "sd_cookie_crttime": "1474344172593",
        "noticeLoginFlag": "1",
        "ptui_loginuin": "yaochao365@qq.com",
        "ptcz": "161d66a2584bb543889fb9aaab854d38726007847b6fd8e79b4d0e85dca74d3a",
        "pt2gguin": "o0959597602",
        "pgv_pvid": "2027905329",
        "o_cookie": "959597602",
        "pac_uid": "1_959597602",
        "wap_sid": "CNPL41MSQHhMbFJmY0JlajliWjQ1bkpDVmZvZ0E3bHpDRHBfZlhmU25tVm9ON3FDMnRoYkJndFRjYWpjZ1hCX3VBU1UxNkgYBCD9ESignp6fCzDsh7i/BQ==",
    }

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse, cookies=self.cookies)

    def parse(self, response):
        dict = json.loads(response.body)
        if dict['errmsg'] == 'ok':
            if dict['count']:
                dict = json.loads(dict['general_msg_list'])
                all_msgs = dict['list']

                # next page
                last_id = all_msgs[-1]['comm_msg_info']['id']
                re_frommsgid = r'frommsgid=(.*?)&'
                frommsgid = re.findall(re_frommsgid, response.url)[0]
                next_url = response.url.replace(str(frommsgid), str(last_id))
                yield Request(next_url, self.parse, cookies=self.cookies)

                for day_msgs in all_msgs:
                    timestamp = day_msgs['comm_msg_info']['datetime']
                    t = time.localtime(timestamp)
                    t = time.strftime('%Y年%m月%d日 %H:%M:%S', t)
                    content_url = day_msgs['app_msg_ext_info']['content_url'].replace('&amp;', '&')
                    title = day_msgs['app_msg_ext_info']['title']
                    multi_app_msg_item_list = day_msgs['app_msg_ext_info']['multi_app_msg_item_list']
                    # 下面的request是大图的msg
                    item = WeixinItem()
                    item['time'] = t
                    item['title'] = title
                    request = Request(url=content_url, callback=self.parse_content, cookies=self.cookies)
                    request.meta['item'] = item
                    yield request

                    # 下面的request是大图下面的msg
                    for msg_item in multi_app_msg_item_list:
                        item = WeixinItem()
                        item['time'] = t
                        title = msg_item['title']
                        item['title'] = title
                        content_url = msg_item['content_url'].replace('&amp;', '&')
                        request = Request(url=content_url, callback=self.parse_content, cookies=self.cookies)
                        request.meta['item'] = item
                        yield request
            else:
                print 'the end...'
        else:
            logger.error(dict['errmsg'])
            re_frommsgid = r'frommsgid=(.*?)&'
            frommsgid = re.findall(re_frommsgid, response.url)[0]
            if dict['errmsg'] == 'no session':
                logger.error('回话过期, 本次回话frommsgid: ' + frommsgid)
            elif dict['errmsg'] == 'req control':
                logger.error('访问被控制, 本次回话frommsgid: ' + frommsgid)
                for i in xrange(1):
                    print '我正在睡觉.' + '.' * i
                    time.sleep(1)
                yield Request(url=response.url, callback=self.parse, dont_filter=True)

    def parse_content(self, response):
        item = response.meta['item']
        js_content = response.xpath('//*[@id="js_content"]')
        contents = js_content.xpath('string(.)').extract()
        text = ''
        for content in contents:
            text = text + content.strip()
        item['text'] = text
        yield item
