# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from fashion_week_crawler.items import GqFashionShowItem
from scrapy.http import Request
import hashlib
import re
import copy


class VoguespiderSpider(CrawlSpider):
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
        brandlists = response.xpath(self.x_path['brandlists'])
        for brandlist in brandlists:
            brands = brandlist.xpath(self.x_path['brands'])
            for brand in brands:
                brand_name = brand.xpath('text()').extract_first()
                item['brand_name'] = brand_name
                item['brand_url'] = brand.xpath('@href').extract_first()
                request = Request(url=item['brand_url'], callback=self.parse_brand_detail_list)
                request.meta['item'] = copy.deepcopy(item)
                yield request

    def parse_brand_detail_list(self, response):
        item = response.meta['item']
        fashion_shows = response.xpath(self.x_path['fashion_shows'])
        for fashion_show in fashion_shows:
            fashionshow_name = fashion_show.xpath(self.x_path['fashionshow_name']).extract_first()
            year = fashionshow_name[0:4]
            season = fashionshow_name[4:]
            item['year'] = year
            item['season'] = season
            item['fashionshow_name'] = fashionshow_name
            item['fashionshow_url'] = fashion_show.xpath(self.x_path['fashionshow_url']).extract_first()
            request = Request(url=item['fashionshow_url'], callback=self.parse_fashion_show_detail)
            request.meta['item'] = copy.deepcopy(item)
            yield request

        # 下一页链接的处理
        next_link = response.xpath(self.x_path['page_next']).extract_first()
        if next_link:
            request = Request(url=next_link, callback=self.parse_brand_detail_list)
            request.meta['item'] = copy.deepcopy(response.meta['item'])
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
        i = 0
        for image_url in images:
            i = i + 1
            image_url = image_url.split('.100X150.jpg')[0]
            md5 = self.md5(image_url)
            image_name = title + str(i)
            item['_id'] = md5
            item['image_name'] = image_name
            item['image_url'] = image_url
            item['comment'] = comment
            item['sex'] = u'男'
            item['city'] = None
            item['type'] = u'高级成衣'
            # yield item

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
