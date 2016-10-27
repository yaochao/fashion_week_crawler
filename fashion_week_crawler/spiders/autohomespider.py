#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/9/30
import json

from scrapy import Request
from scrapy import Spider


class AutohomeSpider(Spider):
    name = 'autohome'
    start_urls = [
        'http://124.202.166.57/cars_v7.1.0/cars/searchcars.ashx?pm=2&minp=0&maxp=0&levels=18%2C19&cids=&gs=&sts=&dsc=&configs=&order=2&pindex=1&psize=1000&bids=&fids=&drives=&seats=&attribute=0'
    ]
    custom_settings = {
        'ITEM_PIPELINES': {
            'fashion_week_crawler.pipelines.AutohomeMongodbPipeline': 100,
        },
    }
    headers1 = {
        'Host': 'cars.app.autohome.com.cn'
    }

    headers2 = {
        'Host': 'koubei.app.autohome.com.cn'
    }

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse, headers=self.headers1)

    def parse(self, response):
        dict = json.loads(response.body)
        if dict['message'] == 'ok':
            seriesitems = dict['result']['seriesitems']
            for seriesitem in seriesitems:
                specitemgroups = seriesitem['specitemgroups']
                seriesitem_id = seriesitem['id']
                seriesname = seriesitem['seriesname']

                koubei_url = 'http://221.193.246.117/autov6.0.0/alibi/seriesalibiinfos-pm2-ss' + str(
                    seriesitem_id) + '-st0-p1-s20.json'
                request = Request(url=koubei_url, callback=self.parse_koubei, headers=self.headers2)
                request.meta['seriesitem_id'] = seriesitem_id
                request.meta['seriesname'] = seriesname
                yield request
                for specitemgroup in specitemgroups:
                    specitems = specitemgroup['specitems']
                    for specitem in specitems:
                        specitem_id = specitem['id']
                        request = Request(url='http://124.202.166.57/cfg_v7.0.0/cars/speccompare.ashx?type=1&cityid=110100&pl=2&specids=' + str(specitem_id), callback=self.parse_config, headers=self.headers1)
                        request.meta['specitem_id'] = specitem_id
                        yield request

    def parse_config(self, response):
        specitem_id = response.meta['specitem_id']
        dict = json.loads(response.body)
        dict['_id'] = specitem_id
        yield dict

    def parse_koubei(self, response):
        seriesitem_id = response.meta['seriesitem_id']
        seriesname = response.meta['seriesname']
        dict = json.loads(response.body)
        list = dict['result']['list']
        average = dict['result']['average']
        yield {'_id': seriesitem_id, 'seriesname': seriesname, 'average': average}
        for i in list:
            Koubeiid = i['Koubeiid']
            koubei_content_url = 'http://221.193.246.117/autov6.0.0/alibi/alibiinfobase-pm2-k'+ str(Koubeiid) +'.json'
            request = Request(url=koubei_content_url, callback=self.parse_koubei_content, headers=self.headers2)
            request.meta['seriesitem_id'] = seriesitem_id
            request.meta['Koubeiid'] = Koubeiid
            yield request
        pagecount = dict['result']['pagecount']
        for i in xrange(pagecount):
            i = i + 1
            koubei_url = 'http://221.193.246.117/autov6.0.0/alibi/seriesalibiinfos-pm2-ss' + str(
                seriesitem_id) + '-st0-p' + str(i) + '-s20.json'
            request = Request(url=koubei_url, callback=self.parse_koubei, headers=self.headers2)
            request.meta['seriesitem_id'] = seriesitem_id
            yield request

    def parse_koubei_content(self, response):
        seriesitem_id = response.meta['seriesitem_id']
        Koubeiid = response.meta['Koubeiid']
        dict = json.loads(response.body)
        dict['seriesitem_id'] = seriesitem_id
        dict['_id'] = Koubeiid
        yield dict
