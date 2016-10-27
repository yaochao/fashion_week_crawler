#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/10/9
import json
import math

from scrapy import Request
from scrapy import Spider


class YicheSpider(Spider):
    name = 'yiche'
    start_urls = [
        'http://42.62.1.156/car/pickcar/?dtshijian=1475994616940&p=0-9999&l=15&g=0&b=0&dt=0&lv=0&t=0&d=&f=0&bd=0&sn=0&m=0000000000000000000000000000&page=1&s=4&pagesize=200',
        'http://42.62.1.156/car/pickcar/?dtshijian=1475994990676&p=0-9999&l=16&g=0&b=0&dt=0&lv=0&t=0&d=&f=0&bd=0&sn=0&m=0000000000000000000000000000&page=1&s=4&pagesize=200'
    ]
    custom_settings = {
        'ITEM_PIPELINES': {
            'fashion_week_crawler.pipelines.YicheMongodbPipeline': 100,
        },
    }

    headers1 = {
        'Host': 'extapi.ycapp.yiche.com'
    }

    headers2 = {
        'Host': 'carapi.ycapp.yiche.com'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse, headers=self.headers1)
        # 获取映射,配置菜单中英文映射
        yield Request(url='http://42.62.1.156/car/getpropertygrouplist', callback=self.parse_propertygrouplist, headers=self.headers2)

    def parse_propertygrouplist(self, response):
        dict = json.loads(response.body)
        yield dict

    def parse(self, response):
        dict = json.loads(response.body)
        if dict['message'] == 'ok':
            car_serial_list = dict['data']['List']
            for car_serial in car_serial_list:
                serialID = car_serial['SerialID']
                serialName = car_serial['Name']
                # 配置
                request = Request(url='http://42.62.1.150/car/GetCarListV61?csid=' + str(serialID), callback=self.parse_carids, headers=self.headers2)
                request.meta['serialID'] = serialID
                request.meta['serialName'] = serialName
                yield request

                # 口碑
                request2 = Request(url='http://42.62.1.150/koubei/GetTopicList?serialID=' + str(
                    serialID) + '&carid=0&pageIndex=1&pageSize=20', callback=self.parse_koubei,
                                   headers=self.headers2)
                request2.meta['serialID'] = serialID
                yield request2

                # 评分
                request = Request(url='http://42.62.1.156/koubei/GetReviewImpression?serialId=' + str(serialID), callback=self.parse_average, headers=self.headers2)
                request.meta['serialName'] = serialName
                request.meta['serialID'] = serialID
                yield request

    def parse_carids(self, response):
        dict = json.loads(response.body)
        serialID = response.meta['serialID']
        serialName = response.meta['serialName']
        carids = ''
        if dict['message'] == u'成功':
            for i in dict['data']:
                car_list = i['CarGroup']['CarList']
                if car_list:
                    for car in car_list:
                        dict = {}
                        carid = car['CarId']
                        name = car['Name']
                        year = car['Year']
                        carname = serialName + ' ' + str(year) + u'款 ' + name
                        dict['_id'] = carid
                        dict['serialid'] = serialID
                        dict['serialName'] = serialName
                        dict['carid'] = carid
                        dict['carname'] = carname
                        yield dict
                        carids += str(carid) + '%2c'

        carids = carids[0: -3]
        request = Request(url='http://42.62.1.150/car/GetCarStylePropertys?carids=' + carids,
                          callback=self.parse_config, headers=self.headers2)
        request.meta['serialID'] = serialID
        request.meta['serialName'] = serialName
        yield request

    def parse_config(self, response):
        dict = json.loads(response.body)
        serialID = response.meta['serialID']
        serialName = response.meta['serialName']
        if dict['message'] == u'成功':
            dict['_id'] = serialID
            dict['serialID'] = serialID
            dict['serialName'] = serialName
            yield dict

    def parse_koubei(self, response):
        dict = json.loads(response.body)
        serialID = response.meta['serialID']
        if dict['message'] == u'成功':
            record_count = dict['data']['RecordCount']
            record_count = int(math.ceil(record_count / 20.0))
            for i in range(record_count):
                i = i + 1
                request = Request(url='http://42.62.1.150/koubei/GetTopicList?serialID=' + str(
                    serialID) + '&carid=0&pageIndex='+ str(i) +'&pageSize=20', callback=self.parse_koubei,
                                   headers=self.headers2)
                request.meta['serialID'] = serialID
                yield request
            dict['serialID_koubei'] = serialID
            yield dict

    def parse_average(self, response):
        dict = json.loads(response.body)
        serialID = response.meta['serialID']
        serialName = response.meta['serialName']
        average = dict['data']['AverageRating']
        if dict['message'] == u'成功':
            yield {'_id':serialID, 'name': serialName, 'average': average}