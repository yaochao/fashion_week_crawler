#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/9/14
import hashlib

import re

import math
from scrapy import Spider, Request

from fashion_week_crawler.items import ULiaoBaoItem


class ULiaoBaoSpider(Spider):
    name = 'uliaobao'
    start_urls = [
        'http://www.uliaobao.com'
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'fashion_week_crawler.pipelines.MongodbStorePipeline': 100,
        }
    }

    def parse(self, response):
        menu_divs = response.xpath('//*[@id="Content_left_menu"]/div')
        for menu_div in menu_divs:
            a_s = menu_div.xpath('div/a')
            for a in a_s:
                item = ULiaoBaoItem()
                item['category'] = a.xpath('text()').extract_first()
                category_url = a.xpath('@href').extract_first()
                category_url = 'http://www.uliaobao.com' + category_url
                request = Request(url=category_url, callback=self.parse_page)
                request.meta['item'] = item
                yield request

    def parse_page(self, response):
        item = response.meta['item']
        li_s = response.xpath('//*[@class="fabricDeil"]')
        for li in li_s:
            url = li.xpath('a/@href').extract_first()
            url = 'http://www.uliaobao.com' + url
            if li.xpath('a/img[@class="tag-pic"]'):
                image_url = li.xpath('a/img[2]/@src').extract_first()
            else:
                image_url = li.xpath('a/img[1]/@src').extract_first()
            image_url = image_url.replace('_200.', '_800.')
            title = li.xpath('div/p/text()').extract_first()
            item['url'] = url
            item['image_url'] = image_url
            item['title'] = title
            item['_id'] = self.md5(url)
            yield item
        # next page
        total_goods = response.xpath('//*[@class="navRight"]/p/span/text()').extract_first()
        total_pages = int(math.ceil(int(total_goods.strip()) / 20.0))
        current_page_number = re.findall(r'page=(.*?)&', response.url)
        current_page_number = int(current_page_number[0])
        print 'total_pages:', total_pages
        print 'current_pages:', current_page_number
        if current_page_number < total_pages:
            next_page_number = current_page_number + 1
            next_url = response.url.replace('page=%s' % str(current_page_number), 'page=%s' % str(next_page_number))
            request = Request(url=next_url, callback=self.parse_page)
            request.meta['item'] = response.meta['item']
            print 'next_page:', next_url
            yield request


    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
