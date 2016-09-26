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
'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MjM5OTAxMTE4MA==&uin=MTc1Njk1MzE1&key=9289b6ec21f92a595ee8811a84c235fd3f13071d778b2bbbc892ca0ecd147eb68c4e3620a1593c5f9ca4c704e879cf7c61f20e2be2f9d545&f=json&frommsgid=1000000072&count=10&uin=MTc1Njk1MzE1&key=9289b6ec21f92a595ee8811a84c235fd3f13071d778b2bbbc892ca0ecd147eb68c4e3620a1593c5f9ca4c704e879cf7c61f20e2be2f9d545&pass_ticket=mbuCaie9VfrohPnPdbxzTWwhAid3Y2cfiMALYKHKmHw%25253D&wxtoken=&x5=1'
    ]

    custom_settings = {
        'FEED_URI': '/Users/yaochao/Desktop/weixin.csv',
        'FEED_FORMAT': 'CSV',
        'ITEM_PIPELINES': {
            'fashion_week_crawler.pipelines.WeiboPipeline': 100,
        },
        'DOWNLOAD_DELAY': 0
    }
    start_time = time.time()

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
                yield Request(next_url, self.parse)

                for day_msgs in all_msgs:
                    timestamp = day_msgs['comm_msg_info']['datetime']
                    t = time.localtime(timestamp)
                    t = time.strftime('%Y年%m月%d日 %H:%M:%S', t)
                    content_url = day_msgs['app_msg_ext_info']['content_url'].replace('&amp;', '&')
                    multi_app_msg_item_list = day_msgs['app_msg_ext_info']['multi_app_msg_item_list']

                    # 下面的request是大图的msg
                    item = WeixinItem()
                    item['time'] = t
                    request = Request(url=content_url, callback=self.parse_content)
                    request.meta['item'] = item
                    yield request

                    # 下面的request是大图下面的msg
                    for msg_item in multi_app_msg_item_list:
                        item = WeixinItem()
                        item['time'] = t
                        content_url = msg_item['content_url'].replace('&amp;', '&')
                        request = Request(url=content_url, callback=self.parse_content)
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
                print time.time() - self.start_time + 's'
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
