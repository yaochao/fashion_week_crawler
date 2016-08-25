# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FashionWeekCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class FashionBrandItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()

class FashionBrandListItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()

class FashionShowItem(scrapy.Item):
    name = scrapy.Field()
    _id = scrapy.Field() # md5(url)
    url = scrapy.Field()
    brand = scrapy.Field()
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()
    comment = scrapy.Field()
    city = scrapy.Field()
    year = scrapy.Field()
    season = scrapy.Field()
    type = scrapy.Field()