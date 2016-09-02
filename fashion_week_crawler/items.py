# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class VogueFashionShowItem(Item):
    _id = Field()  # md5(image_url)
    brand_name = Field()
    brand_url = Field()
    fashionshow_name = Field()
    fashionshow_url = Field()
    image_url = Field()
    image_name = Field()
    comment = Field()
    city = Field()
    year = Field()
    season = Field()
    type = Field()

class GqFashionShowItem(Item):
    _id = Field()  # md5(image_url)
    brand_name = Field()
    brand_url = Field()
    fashionshow_name = Field()
    fashionshow_url = Field()
    image_url = Field()
    image_name = Field()
    comment = Field()
    city = Field()
    year = Field()
    season = Field()
    type = Field()
    sex = Field()

class NoFashionItem(Item):
    _id = Field()  # md5(image_url)
    brand_name = Field()
    subject_url = Field()
    subject_title = Field()
    brand_url = Field()
    fashionshow_name = Field()
    fashionshow_url = Field()
    image_url = Field()
    image_name = Field()
    comment = Field()
    city = Field()
    year = Field()
    season = Field()
    type = Field()
    sex = Field()
