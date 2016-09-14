#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/9/14
import hashlib

from scrapy import Spider, Request

from fashion_week_crawler.items import ULiaoBaoItem


class ULiaoBaoSpider(Spider):
    name = 'uliaobao'
    start_urls = [
        'http://www.uliaobao.com'
    ]

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
            image_url = li.xpath('a/img[2]/@src').extract_first()
            image_url = image_url.replace('200.JPG', '800.JPG')
            title = li.xpath('div/p/text()').extract_first()
            item['url'] = url
            item['image_url'] = image_url
            item['title'] = title
            item['_id'] = self.md5(url)
            yield item

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
