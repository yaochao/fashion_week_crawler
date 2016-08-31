# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib

# import MySQLdb
# import MySQLdb.cursors
# from twisted.enterprise import adbapi
import pymongo
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import os
import logging
from scrapy.utils.project import get_project_settings
from  fashion_week_crawler.items import VogueFashionShowItem, GqFashionShowItem

# settings.py
settings = get_project_settings()


# 存储到Mongodb
class MongodbStorePipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(
            settings['MONGO_HOST'],
            settings['MONGO_PORT']
        )
        self.db = self.client[settings['MONGO_DB']]
        self.collection_vogue = self.db[settings['MONGO_COLLECTION_VOGUE']]
        self.collection_gq = self.db[settings['MONGO_COLLECTION_GQ']]

    def process_item(self, item, spider):
        if type(item) == VogueFashionShowItem:
            collection = self.collection_vogue
        else:
            collection = self.collection_gq

        try:
            collection.insert(dict(item))
        except Exception as e:
            logger = logging.getLogger('MongodbStorePipeline')
            logger.error(e)
        return item

    def close_spider(self, spider):
        self.client.close()


# 检测图片是否存在
class DuplicatesImagePipeline(object):
    def process_item(self, item, spider):
        if type(item) == VogueFashionShowItem:
            basepath = settings['IMAGES_STORE'] + 'vogue/'
        else:
            basepath = settings['IMAGES_STORE'] + 'gq/'

        filename = item['_id'] + '.jpg'
        filepath = basepath + filename
        if os.path.exists(filepath):
            raise DropItem("Image already exists")
        else:
            return item


# 保存图片 Pipeline ,优先级:300
class SaveImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield Request(item['image_url'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item

    def file_path(self, request, response=None, info=None):
        if not isinstance(request, Request):
            url = request
        else:
            url = request.url
        if url.find('vogueimg') != -1:
            folder = 'vogue/'
        else:
            folder = 'gq/'
        return folder + self.md5(url) + '.jpg'

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
