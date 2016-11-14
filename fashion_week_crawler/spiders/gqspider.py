# -*- coding: utf-8 -*-
import copy
import hashlib
import re

from scrapy.http import Request
from scrapy.spiders import CrawlSpider

from fashion_week_crawler.items import GqFashionShowItem


class GqSpider(CrawlSpider):
    name = "gq"
    start_urls = (
        'http://shows.gq.com.cn/',
    )

    x_path = {
        'brandlists': '//div[@id="js-retrieval-scroll"]/div[2]/div[2]',
        'brands': 'div/div/a',
        'fashion_shows': '//h3',
        'fashionshow_name': 'a/em/text()',
        'fashionshow_url': 'a/@href',
        'page_next': '//a[@class="page-next"]/@href',
        'image_title': '//div[@class="links"]/a/text()',
        'images': '//div[@class="listBox"]/div[2]/div/ul/li',
        'comments': '//div[@class="text"]/text()',
    }

    def parse(self, response):
        item = GqFashionShowItem()
        a_s = response.xpath('//div[@id="js-shows-scroll"]/div[@class="select-cont"]/div[@class="viewport"]/div/div/a')
        for a in a_s:
            href = a.xpath('@href').extract_first()
            item['page_url'] = href
            request = Request(url=href, callback=self.parse_brand_list)
            request.meta['item'] = copy.deepcopy(item)
            yield request


    def parse_brand_list(self, response):
        item = response.meta['item']
        picitems = response.xpath('//div[@class="item pic-item"]')
        for picitem in picitems:
            href = picitem.xpath('a/@href').extract_first()
            title = picitem.xpath('img/@alt').extract_first()
            brand = picitem.xpath('span/text()').extract_first()
            year = title.split(brand)[1][:4]
            city = title.split(brand)[1][4:6]
            season = title.split(brand)[1][6:8]
            item['brand_name'] = brand
            item['year'] = year
            item['season'] = season
            item['city'] = city
            item['fashionshow_name'] = title
            item['fashionshow_url'] = href
            request = Request(url=href, callback=self.parse_fashion_show_detail)
            request.meta['item'] = copy.deepcopy(item)
            yield request

    def parse_fashion_show_detail(self, response):
        item = response.meta['item']
        # 提取标题
        title = response.xpath(self.x_path['image_title']).extract_first()

        # 提取评论
        comments = response.xpath(self.x_path['comments']).extract()
        comment = None
        if comments:
            for comm in comments:
                if comm.strip():
                    comment = comment + comm.strip() + ','

        # 提取图片, url在下面的字符串里面
        # var tshowsData = ["http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00050big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00060big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00090big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00100big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00130big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showMEN/YYADIDASMEN/RUNWAY/00410big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00460big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00490big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00520big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00530big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00540big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00550big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00560big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00570big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00580big.jpg.100X150.jpg","http://shows.gqimg.com.cn/showspic/FashionImages/F2011MEN/YYADIDASMEN/RUNWAY/00630big.jpg.100X150.jpg"];
        images_re = r'var tshowsData = \["(.*?)"\];'
        images_str = re.findall(images_re, response.body)[0]
        images = images_str.split('","')
        for i, image_url in enumerate(images):
            image_url = image_url.split('.100X150.jpg')[0]
            md5 = self.md5(image_url)
            image_name = title + str(i)
            item['_id'] = md5
            item['image_name'] = image_name
            item['image_url'] = image_url
            item['comment'] = comment
            item['sex'] = u'男'
            item['type'] = None
            yield item

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
