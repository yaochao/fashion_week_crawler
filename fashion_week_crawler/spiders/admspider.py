#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/11/18

from scrapy import Spider, Request
from fashion_week_crawler.items import AdmItem
from fashion_week_crawler.misc.encryption import md5

class AdmSpider(Spider):
    name = 'adm'
    start_urls = ['http://www.hzadm.com/site/adm/guest/index.html',
                  'http://www.hzadm.com/site/adm/guest/index_1.html',
                  'http://www.hzadm.com/site/adm/guest/index_2.html',
                  'http://www.hzadm.com/site/adm/guest/index_3.html',
                  'http://www.hzadm.com/site/adm/guest/index_4.html',
                  ]
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'fashion_week_crawler.pipelines.AdmMysqlPipeline': 100,
            'fashion_week_crawler.pipelines.AdmImagePipeline': 200,
        },
        'IMAGES_STORE': '/Users/yaochao/Pictures/Adm/'
    }

    def parse(self, response):
        url = response.url
        print url
        divs = response.xpath('//*[@class="fg_hover"]')
        for div in divs:
            item = AdmItem()
            img_url = div.xpath('img/@src').extract_first()
            img_url = 'http://www.hzadm.com' + img_url
            name = div.xpath('a/div[@class="fg_item_con"]/h4/text()').extract_first()
            intro = div.xpath('a/div[@class="fg_item_con"]/p/text()').extract_first()
            item['_id'] = md5(img_url)
            item['img_url'] = img_url
            item['name'] = name
            item['intro'] = intro
            yield item
