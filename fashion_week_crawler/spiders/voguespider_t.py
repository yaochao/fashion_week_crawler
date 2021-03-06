# -*- coding: utf-8 -*-
import copy
import hashlib
import json
import logging
import re
import urllib2

import scrapy
from scrapy.spiders import CrawlSpider

from fashion_week_crawler.items import VogueFashionShowItem


class VoguespiderSpider(CrawlSpider):
    name = "vogue_t"
    start_urls = (
        'http://shows.vogue.com.cn/all.html',
    )

    # 自定义设置,会覆盖项目级别的settings
    custom_settings = {
        'ITEM_PIPELINES': {
            'fashion_week_crawler.pipelines.VogueMongodbStorePipeline': 100,
            # 'fashion_week_crawler.pipelines.DuplicatesImagePipeline': 200,
            # 'fashion_week_crawler.pipelines.SaveImagesPipeline': 300,
        }
    }

    x_query = {
        'namelists': '//div[@class="nameList"]',
        'brands': 'ul/li',
        'brand_name': 'a/text()',
        'brand_url': 'a/@href',
        'fashion_shows': '//div[@class="xcl-p6"]',
        'fashionshow_name': 'div/h2/text()',
        'fashionshow_url': 'div/p/a/@href',
        'next_link_re': r'<a  href=\'(.*?)\' >下一页',
        'title': '//div[@class="xc-list-tt"]/h1/a/text()',
        'city_list': '//*[@id="main"]/div[2]/div[1]/p[2]/a[2]/text()',
        'type_sel': '//*[@id="main"]/div[2]/div[1]/p[2]/a[1]/text()',
        'comment_sel': '//div[@class="content"]/div[@class="section xcl-text"]/div[@class="txt"]/text()',
        'photos_mark': '//ul[@class="bd"]/li[@class="item"]',
        'data_url': '//*[@class="fullscreen"]/param[2]/@value',
    }

    def parse(self, response):
        item = VogueFashionShowItem()
        namelists = response.xpath(self.x_query['namelists'])
        for namelist in namelists:
            brands = namelist.xpath(self.x_query['brands'])
            for brand in brands:
                item['brand_name'] = brand.xpath(self.x_query['brand_name']).extract_first()
                item['brand_url'] = brand.xpath(self.x_query['brand_url']).extract_first()
                request = scrapy.Request(url=item['brand_url'], callback=self.parse_brand_detail_list)
                request.meta['item'] = copy.deepcopy(item)
                yield request

    def parse_brand_detail_list(self, response):
        item = response.meta['item']
        fashion_shows = response.xpath(self.x_query['fashion_shows'])
        for fashion_show in fashion_shows:
            item['fashionshow_name'] = fashion_show.xpath(self.x_query['fashionshow_name']).extract_first()
            fashionshow_url = fashion_show.xpath(self.x_query['fashionshow_url']).extract_first() + 'runway/'
            request = scrapy.Request(url=fashionshow_url, callback=self.parse_fashionshow_detail_site)
            request.meta['item'] = copy.deepcopy(item)
            yield request

        # 下一页链接的处理
        rst = re.findall(self.x_query['next_link_re'], response.body)
        if rst:
            next_link = rst[0].split('href=\'')[-1]
            request = scrapy.Request(url=next_link, callback=self.parse_brand_detail_list)
            request.meta['item'] = copy.deepcopy(response.meta['item'])
            yield request

    def parse_fashionshow_detail_site(self, response):
        item = response.meta['item']
        item['fashionshow_url'] = response.xpath('//div[@class="content"]/div/ul/li/a/@href').extract_first()
        request = scrapy.Request(url=item['fashionshow_url'], callback=self.parse_fashion_show_detail)
        request.meta['item'] = copy.deepcopy(item)
        yield request

    def parse_fashion_show_detail(self, response):
        item = response.meta['item']
        title = response.xpath(self.x_query['title']).extract()
        if len(title) == 0:
            logger = logging.getLogger('parse_fashion_show_detail')
            logger.warning('页面不存在%s' % response.url)
            return
        title = title[0]
        title_sp = title.split('20')
        img_title = '20' + title_sp[1]

        # 提取city, year, season
        city_list = response.xpath(self.x_query['city_list']).extract()
        city = ''
        year = ''
        season = ''
        if len(city_list) != 0:
            city_1 = city_list[0]  # '2016巴黎秋冬时装发布'

            re_a = r'^(20\d{2})(.*)(春夏|秋冬)(时装|婚纱)发布$'.decode('utf-8')
            rests = re.findall(re_a, city_1)
            year = rests[0][0]
            city = rests[0][1]
            season = rests[0][2]

        # 提取 type: 高级成衣 高级定制 婚纱
        type_sel = response.xpath(self.x_query['type_sel']).extract()
        type = ''
        if len(type_sel) != 0:
            type_1 = type_sel[0]  # '2016秋冬高级成衣/高级定制/婚纱发布秀'
            re_type = r'^(20\d{2})(.*)(高级成衣|高级定制|婚纱)发布秀$'.decode('utf-8')
            rests = re.findall(re_type, type_1)
            type = rests[0][2]

        # 提取评论
        comment_sel = response.xpath(self.x_query['comment_sel']).extract()
        comment = ''
        if len(comment_sel) != 0:
            for comm in comment_sel:
                if comm.strip() != '':
                    comment = comment + comm.strip() + ','

        # # 提取小图片
        # photos = response.xpath('//ul[@class="bd"]/li[@class="item"]')
        # for photo in photos:
        #     url = photo.xpath('img/@crs').extract()[0]

        # 提取原始大图
        data_url = response.xpath(self.x_query['data_url']).extract_first().split('&')[2].split('=')[-1]
        res = urllib2.urlopen(data_url)
        photos = json.loads(res.read())
        photos = photos['slides']
        for photo in photos:
            image_url = photo['src']
            md5 = self.md5(image_url)
            item['image_name'] = img_title + str(photos.index(photo) + 1)
            item['image_url'] = image_url
            item['_id'] = md5
            item['comment'] = comment
            item['city'] = city
            item['year'] = year
            item['type'] = type
            item['season'] = season
            yield item

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
