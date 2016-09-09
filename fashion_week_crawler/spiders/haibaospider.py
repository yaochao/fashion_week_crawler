#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/9/9

import copy
import hashlib

from scrapy import Request
from scrapy.spiders import Spider

from fashion_week_crawler.items import HaibaoItem


class HaibaoSpider(Spider):
    name = 'haibao'
    start_urls = [
        'http://brand.haibao.com/fashion/324'
    ]

    def parse(self, response):
        item = HaibaoItem()
        uls = response.xpath('//div[@class="listlabel lab_new"]/ul')
        for ul in uls:
            lis = ul.xpath('li')
            for li in lis:
                page_url = li.xpath('div/a/@href').extract_first()
                page_url = page_url.split('/')[-1]
                page_url = 'http://pic.haibao.com/brand/article/' + page_url
                item['fashionshow_url'] = page_url
                item['fashionshow_name'] = li.xpath('div/a/img/@title').extract_first()
                item['index_url'] = response.url
                request = Request(url=item['fashionshow_url'], callback=self.parse_fashionshow)
                request.meta['item'] = copy.deepcopy(item)
                yield request

        # next page
        next_url = response.xpath('//a[@class="next "]/@href').extract_first()
        if next_url:
            yield Request(url=next_url, callback=self.parse)

    def parse_fashionshow(self, response):
        item = response.meta['item']
        image_urls = response.xpath('//li[@class="jsImageUrlList"]/a/img/@imgurl').extract()
        image_descs = response.xpath('//li[@class="jsImageUrlList"]/a/img/@desc').extract()
        for image_url in image_urls:
            item['_id'] = self.md5(image_url)
            item['image_url'] = image_url
            item['image_name'] = image_descs[0] + ' - ' +str(image_urls.index(image_url))
            yield item

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()