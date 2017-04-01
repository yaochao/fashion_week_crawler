# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/10/31

import requests
import xlwt
from scrapy import Spider
from scrapy.http import Request


class BaiduSpider(Spider):
    name = 'baidu'
    url = 'http://www.baidu.com/s?wd=%E5%AE%9D%E9%A9%AC5%E7%B3%BB%E6%A0%B7%E8%BD%A6%E5%88%86%E6%9E%90&pn='
    custom_settings = {
        # 'DOWNLOAD_DELAY': 0.5,
        'REDIRECT_ENABLED': True,
    }

    def __init__(self):
        self.xls = xlwt.Workbook()
        self.sheet = self.xls.add_sheet("sheet1")
        self.sheet.write(0, 0, 'title')
        self.sheet.write(0, 1, 'url')

    def start_requests(self):

        keyword = '宝马5系样车分析'
        request = Request(
            url=self.url + '0'
        )
        yield request

    i = 0
    ii = 0

    def parse(self, response):

        result_divs = response.xpath('//div[@class="result c-container "]')
        if not result_divs:
            print(response.text)
            return
        for index, result_div in enumerate(result_divs):

            title = result_div.xpath('h3[@class="t"]')
            url = result_div.xpath('h3[@class="t"]/a/@href').extract_first()
            if url:
                result = requests.get(url, allow_redirects=False)
                url = result.headers['Location']
                print(url)

            if title:
                title = title[0].xpath('string(.)').extract_first()

            if u'宝马5系' in title:
                if u'评测' in title or u'分析' in title:
                    # 写到xlsx
                    self.ii = self.ii + 1
                    self.sheet.write(self.ii, 0, title)
                    self.sheet.write(self.ii, 1, url)


        # next_url
        self.i = self.i + 1
        if self.i == 70:
            self.xls.save('baidu_results.xls')
            return
        next_url = self.url + str(self.i * 10)
        request = Request(url=next_url)
        yield request
