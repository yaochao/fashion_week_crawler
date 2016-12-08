#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by yaochao on 2016/9/30
import json

from scrapy import Request
from scrapy import Spider


class AutohomeSpider(Spider):
    name = 'autohome2'
    start_urls = [
        'http://sou2.api.autohome.com.cn/wrap/souche/?cs=1&ignores=content&size=50&tm=app&um=list_ranking&q='
    ]
    custom_settings = {
        'ITEM_PIPELINES': {
            'fashion_week_crawler.pipelines.AutohomePipeline': 100,
            'fashion_week_crawler.pipelines.AutohomeKafkaPipeline': 200,
        },
    }

    headers1 = {
        'Host': 'cars.app.autohome.com.cn'
    }

    headers2 = {
        'Host': 'mobile.app.autohome.com.cn'
    }

    headers3 = {
        'Host': 'app.k.autohome.com.cn'
    }

    koubei_header_pc = {
        'Host': 'k.autohome.com.cn'
    }

    koubei_header_app = {
        'Host': 'koubei.app.autohome.com.cn'
    }

    carnames = ['比亚迪S7', '瑞风S7', 'CS95', '传祺GS8', '力帆X80', '东南DX9']
    # carnames = ['比亚迪S7']

    def start_requests(self):
        for i in self.carnames:
            url = self.start_urls[0] + i
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.body)
        result = result['result']
        if result:
            carid = result['list'][0]['id']
            # 口碑,从App接口获取
            koubei_url_app = 'http://121.22.246.106/autov6.0.0/alibi/seriesalibiinfos-pm2-ss' + str(
                carid) + '-st0-p1-s20.json'
            request = Request(url=koubei_url_app, callback=self.parse_koubei_list_app, headers=self.koubei_header_app)
            request.meta['carid'] = carid
            yield request

            # 购买目的,单独从Web上提出来
            koubei_url_pc = 'http://k.autohome.com.cn/' + str(carid)
            request = Request(url=koubei_url_pc, callback=self.parse_koubei_list_pc, headers=self.koubei_header_pc)
            request.meta['carid'] = carid
            yield request

            # 配置, 从App接口提取
            config_url = 'http://124.202.166.57/carinfo_v7.3.0/cars/seriessummary-pm2-s' + str(carid) + '-t-c110100.json'
            request = Request(config_url, callback=self.parse_car_specids, headers=self.headers1)
            request.meta['carid'] = carid
            yield request

            # 故障 detail
            trouble_url = 'http://124.164.9.98/quality_v5.6.0/quality/qualitycategorypercent-sid'+str(carid)+'-t1.json'
            request = Request(url=trouble_url, callback=self.parse_trouble_list, headers=self.headers2)
            request.meta['carid'] = carid
            yield request

            # 故障 rank
            trouble_url2 = 'http://app.k.autohome.com.cn/' + str(carid) + '/appquality?type=1'
            request = Request(url=trouble_url2, callback=self.parse_trouble_rank)
            request.meta['carid'] = carid
            yield request

    def parse_trouble_rank(self, response):
        print response.url
        carid = response.meta['carid']
        lis = response.xpath('//section[@class="list-quality"]/ul/li')
        trouble_rank = []
        for index, li in enumerate(lis):
            if index != 0:
                rank = li.xpath('span/i/text()').extract_first()
                trouble_name = li.xpath('span/em/text()').extract_first()
                trouble_count = li.xpath('span[2]/text()').extract_first()
                trouble_rank.append([rank, trouble_name, trouble_count])
        yield {
            '_id': carid,
            'carid': carid,
            'trouble_rank': trouble_rank,
            'type': 'trouble_rank',
        }

    # 根据carid, 解析出这种car的故障
    def parse_trouble_list(self, response):
        carid = response.meta['carid']
        result = json.loads(response.body)['result']
        for trouble in result:
            detail_url = trouble['url']
            request = Request(url=detail_url, callback=self.parse_trouble_detail)
            request.meta['trouble'] = trouble
            request.meta['carid'] = carid
            yield request

    def parse_trouble_detail(self, response):
        carid = response.meta['carid']
        trouble = response.meta['trouble']
        lis = response.xpath('//ul/li')
        v = []
        for li in lis:
            if li.xpath('div'):
                kk = li.xpath('h6/text()').extract_first()
                vv = []
                spans = li.xpath('div/span')
                for span in spans:
                    text = span.xpath('text()').extract_first()
                    text = text.split(' (')
                    kkk = text[0]
                    vvv = text[1][0:-1]
                    vv.append({kkk: vvv})
            else:
                text = li.xpath('h6/text()').extract_first()
                text = text.split(' (')
                kk = text[0]
                vv = text[1][0:-1]
            v.append({kk: vv})
        trouble['detail'] = v
        trouble['type'] = 'trouble_detail'
        trouble['carid'] = carid
        yield trouble

    # 根据carid, 解析出同一车型不同配置的car的id(specid)
    def parse_car_specids(self, response):
        carid = response.meta['carid']
        result = json.loads(response.body)
        enginelist = result['result']['enginelist']
        specidstr = ''
        for engine in enginelist:
            speclist = engine['speclist']
            for spec in speclist:
                specid = spec['id']
                specidstr += (str(specid) + ',')
        specidstr = specidstr[0: len(specidstr) - 1]
        # 配置, 从App接口提取
        request = Request(
            url='http://124.202.166.57/cfg_v7.0.0/cars/speccompare.ashx?type=1&cityid=110100&pl=2&specids=' + specidstr,
            callback=self.parse_config, headers=self.headers1)
        request.meta['carid'] = carid
        yield request

    # 根据specidstr(25484,25485,25486,25487,25488,24836,25483)获取同一型号不同配置的车型的所有配置项
    def parse_config(self, response):
        carid = response.meta['carid']
        result = json.loads(response.body)
        result['_id'] = carid
        result['type'] = 'config'
        yield result

    def parse_koubei_list_app(self, response):
        carid = response.meta['carid']
        result = json.loads(response.body)
        list = result['result']['list']
        for i in list:
            koubeiid = i['Koubeiid']
            koubei_content_url = 'http://121.22.246.106/autov6.0.0/alibi/alibiinfobase-pm2-k' + str(koubeiid) + '.json'
            request = Request(url=koubei_content_url, callback=self.parse_koubei_content_app,
                              headers=self.koubei_header_app)
            request.meta['koubeiid'] = koubeiid
            yield request

        # next page
        pagecount = result['result']['pagecount']
        for i in range(pagecount):
            i = i + 1
            koubei_url = 'http://121.22.246.106/autov6.0.0/alibi/seriesalibiinfos-pm2-ss' + str(
                carid) + '-st0-p' + str(i) + '-s20.json'
            request = Request(url=koubei_url, callback=self.parse_koubei_list_app, headers=self.koubei_header_app)
            request.meta['carid'] = carid
            yield request

    def parse_koubei_content_app(self, response):
        koubeiid = response.meta['koubeiid']
        result = json.loads(response.body)
        result['_id'] = koubeiid
        result['type'] = 'koubei'
        yield result

    def parse_koubei_list_pc(self, response):
        carid = response.meta['carid']
        mouthcons = response.xpath('//div[@class="mouthcon"]')
        for mouthcon in mouthcons:
            userid = mouthcon.xpath('div/div/div/div/div/div/a/@href').extract_first()
            userid = userid.split('/')[-1]
            purchase_goal = mouthcon.xpath('div/div/div[2]/dl[@class="choose-dl border-b-no"]/dd')[0].xpath(
                'string(.)').extract_first()
            purchase_goal = purchase_goal.split()
            result = {}
            result['carid'] = carid
            result['userid'] = userid
            result['purchase_goal'] = purchase_goal
            result['type'] = 'purchase_goal'
            yield result

        next_url = response.xpath('//a[@class="page-item-next"]/@href').extract_first()
        if next_url:
            next_url = 'http://k.autohome.com.cn/' + next_url
            request = Request(url=next_url, callback=self.parse_koubei_list_pc)
            request.meta['carid'] = carid
            yield request
