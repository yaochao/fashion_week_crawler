#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/10/31

from scrapy import Spider
from scrapy.http import Request
import xlwt, requests


class BaiduSpider(Spider):
    name = 'baidu'
    url = 'http://www.baidu.com/s?wd=%E6%97%B6%E5%B0%9A%E4%BA%A7%E4%B8%9A%E5%A4%A7%E6%95%B0%E6%8D%AE%E5%BA%94%E7%94%A8%E7%B3%BB%E7%BB%9FDPF2.0%E4%BA%AE%E7%9B%B8%E6%96%87%E5%8D%9A%E4%BC%9A&oq=%E6%97%B6%E5%B0%9A%E4%BA%A7%E4%B8%9A%E5%A4%A7%E6%95%B0%E6%8D%AE%E5%BA%94%E7%94%A8%E7%B3%BB%E7%BB%9FDPF2.0%E4%BA%AE%E7%9B%B8%E6%96%87%E5%8D%9A%E4%BC%9A&ie=utf-8&pn='
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'REDIRECT_ENABLED': True,
    }

    def __init__(self):
        self.xls = xlwt.Workbook()
        self.sheet = self.xls.add_sheet("sheet1")
        self.sheet.write(0, 0, 'title')
        self.sheet.write(0, 1, 'url')
        self.sheet.write(0, 2, 'type')

    def start_requests(self):

        keyword = '时尚产业大数据应用系统DPF2.0亮相文博会'
        request = Request(
            url=self.url + '0'
        )
        yield request

    i = 0
    ii = 0
    def parse(self, response):

        result_divs = response.xpath('//div[@class="result c-container "]')
        print result_divs
        if not result_divs:
            print(response.text)
            return
        for index, result_div in enumerate(result_divs):
            self.ii = self.ii + 1

            type = u'主要发表'
            title = result_div.xpath('h3[@class="t"]')
            url = result_div.xpath('h3[@class="t"]/a/@href').extract_first()
            if url:
                result = requests.get(url, allow_redirects=False)
                # url = result.headers['Location']
                print result.headers
                print result.text

            if title:
                title = title[0].xpath('string(.)').extract_first()
                if u'时尚产业大数据应用系统' not in title:
                    type = u'引用发表'
            # 写到xlsx
            self.sheet.write(self.ii , 0, title)
            self.sheet.write(self.ii, 1, url)
            self.sheet.write(self.ii, 2, type)


        # next_url
        self.i = self.i + 1
        if self.i == 18:
            self.xls.save('baidu_results.xls')
            return
        next_url = self.url + str(self.i * 10)
        request = Request(url=next_url)
        yield request



