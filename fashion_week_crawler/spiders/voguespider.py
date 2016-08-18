# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from fashion_week_crawler.items import FashionBrandItem, FashionBrandListItem, FashionShowItem
from scrapy.selector import Selector
import scrapy
import hashlib
import re


class VoguespiderSpider(CrawlSpider):
    name = "vogue"
    start_urls = (
        'http://shows.vogue.com.cn/all.html',
    )
    # 自定义设置
    # custom_settings = {
    #     'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
    # }

    def parse(self, response):
        fashion_brand_item = FashionBrandItem()
        selector = Selector(response)
        namelists = selector.xpath('//div[@class="nameList"]')
        for namelist in namelists:
             brands = namelist.xpath('ul/li')
             for brand in brands:
                 name = brand.xpath('a/text()').extract()
                 url = brand.xpath('a/@href').extract()
                 fashion_brand_item['name'] = name[0]
                 fashion_brand_item['url'] = url[0]
                 yield scrapy.Request(url=url[0], callback=self.parse_brand_detail_list)

    def parse_brand_detail_list(self, response):
        fashion_brand_list_item = FashionBrandListItem()
        selector = Selector(response)
        fashion_shows = selector.xpath('//div[@class="xcl-p6"]')
        for fashion_show in fashion_shows:
            name = fashion_show.xpath('div/h2/text()').extract()
            url = fashion_show.xpath('div/p/a/@href').extract()
            fashion_brand_list_item['name'] = name[0]
            fashion_brand_list_item['url'] = url[0]
            with open('allfashionshow.txt', 'a') as f:
                f.write(url[0]+'\n')
            yield scrapy.Request(url=url[0], callback=self.parse_fashion_show_detail)

        # 下一页链接的处理
        next_link_re = r'<a  href=\'(.*?)\' >下一页'
        rst = re.findall(next_link_re, response.body)
        if rst:
            next_link = rst[0].split('href=\'')[-1]
            yield scrapy.Request(url=next_link, callback=self.parse_brand_detail_list)


    def parse_fashion_show_detail(self, response):
        fashion_show_item = FashionShowItem()
        selector = Selector(response)
        title = selector.xpath('//div[@class="xc-list-tt"]/h1/a/text()').extract()
        if len(title) == 0:
            print '页面不存在%s' % response.url
            return
        title = title[0]
        title_sp = title.split('20')
        brand = title_sp[0]
        img_title = '20' + title_sp[1]

        # 提取city, year, season
        city_list = selector.xpath('//*[@id="main"]/div[2]/div[1]/p[2]/a[2]/text()').extract()
        city = ''
        year = ''
        season = ''
        if len(city_list) !=0:
            city_1 = city_list[0] # '2016巴黎秋冬时装发布'
            # city_2 = city_1[4:]   # '巴黎秋冬时装发布'
            # position = len(city_2) - 6 # 一共6个汉字(春夏/秋冬时装发布) ,6*3=18
            # city = city_2[0:position] # '巴黎'
            #
            # year = city_1[0:4] # '2016'
            #
            # position2 = len(city_2) - 4 # 一共6个汉字(时装发布) ,4*3=18
            # season = city_2[position2-2:position2]

            re_a = r'^(20\d{2})(.*)(春夏|秋冬)(时装|婚纱)发布$'.decode('utf-8')
            rests = re.findall(re_a, city_1)
            year = rests[0][0]
            city = rests[0][1]
            season = rests[0][2]

        # 提取 type: 高级成衣 高级定制 婚纱
        type_sel = selector.xpath('//*[@id="main"]/div[2]/div[1]/p[2]/a[1]/text()').extract()
        type = ''
        if len(type_sel) != 0:
            type_1 = type_sel[0] # '2016秋冬高级成衣/高级定制/婚纱发布秀'
            re_type = r'^(20\d{2})(.*)(高级成衣|高级定制|婚纱)发布秀$'.decode('utf-8')
            rests = re.findall(re_type, type_1)
            type = rests[0][2]
            print rests, type

        # 提取评论
        comment_sel = selector.xpath('//div[@class="content"]/div[@class="section xcl-text"]/div[@class="txt"]/text()').extract()
        comment = ''
        if len(comment_sel) !=0:
            for comm in comment_sel:
                if comm.strip() != '':
                    comment = comment + comm.strip() + ','

        # 提取图片
        photos = selector.xpath('//ul[@class="bd"]/li[@class="item"]')
        for photo in photos:
            url = photo.xpath('img/@crs').extract()[0]
            url_sp = url.split('#')
            url = url_sp[0]
            md5 = self.md5(url)
            name = img_title + url_sp[1]
            fashion_show_item['name'] = name
            fashion_show_item['url'] = url
            fashion_show_item['md5'] = md5
            fashion_show_item['brand'] = brand
            fashion_show_item['comment'] = comment
            fashion_show_item['city'] = city
            fashion_show_item['year'] = year
            fashion_show_item['type'] = type
            fashion_show_item['season'] = season
            with open('allimage.txt', 'a') as f:
                f.write(fashion_show_item['md5']+'.jpg\n')
            yield fashion_show_item

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()