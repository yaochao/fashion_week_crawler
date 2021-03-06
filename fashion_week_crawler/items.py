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
    page_url = Field()
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


class HaibaoItem(Item):
    _id = Field()  # md5(image_url)
    brand_name = Field()
    index_url = Field()
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

class LadyMaxItem(Item):
    _id = Field()  # md5(image_url)
    brand_name = Field()
    index_url = Field()
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

class ULiaoBaoItem(Item):
    _id = Field()
    category_url = Field()
    url = Field()
    category = Field()
    title = Field()
    image_url = Field()

class WeiboItem(Item):
    text = Field()
    time = Field()

class WeixinItem(Item):
    text = Field()
    time = Field()
    title = Field()

class AdmItem(Item):
    _id = Field()
    img_url = Field()
    name = Field()
    intro = Field()