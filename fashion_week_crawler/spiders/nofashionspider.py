# -*- coding: utf-8 -*-
import copy
import hashlib
import re

from scrapy.http import Request
from scrapy.spiders import CrawlSpider

from fashion_week_crawler.items import NoFashionItem


class NoFashionSpider(CrawlSpider):
    name = "nofashion"
    start_urls = (
        'http://www.nofashion.cn/t/menu.html',
    )

    citys = ['巴黎', '巴黎', '米兰', '伦敦', '纽约', '东京', '柏林', '伦敦', '米兰', '巴黎', '纽约', '佛罗伦萨', '北京', '上海', '', '']
    sexs = ['女装', '女装', '女装', '女装', '女装', '女装', '女装', '男装', '男装', '男装', '男装', '男装', '女装', '女装', '女装', '女装', ]
    x_path = {
        'brands': 'div/div/a',
        'fashion_shows': '//div[@class="data hide"]/ul/li',
        'fashionshow_name': 'span[2]/a/text()',
        'fashionshow_url': 'span[2]/a/@href',
        'page_next': '//*[@class="next"]/a/@href',
        'image_title': '//title/text()',
        'images': '//div[@class="listBox"]/div[2]/div/ul/li',
        'detail_page_next': '//li[@class="next"]/a/@href',
    }

    def parse(self, response):
        item = NoFashionItem()
        # 解析
        a = response.body.split('#T台:\n')[1]
        b = a.split(',\n#')[0]
        c = b.split(',\n')
        for d in c:
            e = d.strip().replace('\t', '')
            f = e.split('_')
            url = 'http://www.nofashion.cn/c/' + f[1] + '.html'
            title = f[0]
            item['subject_url'] = url
            item['subject_title'] = title
            item['city'] = self.citys[c.index(d)]
            item['sex'] = self.sexs[c.index(d)]
            request = Request(url, callback=self.parse_subject_detail_list)
            request.meta['item'] = copy.deepcopy(item)
            yield request

    def parse_subject_detail_list(self, response):
        item = response.meta['item']
        fashion_shows = response.xpath(self.x_path['fashion_shows'])
        for fashion_show in fashion_shows:
            fashionshow_name = fashion_show.xpath(self.x_path['fashionshow_name']).extract_first()
            item['year'] = re.findall(r'(20\d{2})', fashionshow_name)[0]
            item['fashionshow_name'] = fashionshow_name
            item['fashionshow_url'] = fashion_show.xpath(self.x_path['fashionshow_url']).extract_first()
            request = Request(url=item['fashionshow_url'], callback=self.parse_fashion_show_detail)
            request.meta['item'] = copy.deepcopy(item)
            # print item
            yield request

        # 下一页链接的处理
        next_link = response.xpath(self.x_path['page_next']).extract_first()
        if next_link:
            next_link = 'http://www.nofashion.cn' + next_link
            request = Request(url=next_link, callback=self.parse_subject_detail_list)
            request.meta['item'] = copy.deepcopy(response.meta['item'])
            yield request

    def parse_fashion_show_detail(self, response):
        item = response.meta['item']
        # 提取标题
        title = response.xpath(self.x_path['image_title']).extract_first()
        title = title.split(' - ')[0]

        # 提取图片, url在下面的字符串里面
        images_div = response.xpath('//div[@class="endText"]/p')
        i = 0
        for div in images_div:
            i = i + 1
            image_url = div.xpath('img/@src').extract_first()
            if image_url:
                md5 = self.md5(image_url)
                image_name = title + str(i)
                item['_id'] = md5
                item['image_name'] = image_name
                item['image_url'] = image_url
                yield item

            # 下一页链接的处理
            next_link = response.xpath(self.x_path['detail_page_next']).extract_first()
            if next_link:
                next_link = 'http://www.nofashion.cn/' + next_link
                request = Request(url=next_link, callback=self.parse_fashion_show_detail)
                request.meta['item'] = copy.deepcopy(response.meta['item'])
                yield request

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
