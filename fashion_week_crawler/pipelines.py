# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import json
import logging
import os

import MySQLdb
import pymongo
from kafka import KafkaProducer
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

from  fashion_week_crawler.items import VogueFashionShowItem, GqFashionShowItem, NoFashionItem, HaibaoItem

# settings.py
settings = get_project_settings()
logger = logging.getLogger(__name__)


# weibo pipeline
class WeiboPipeline(object):
    def process_item(self, item, spider):
        return item


# autohome mongodb pipeline
class YicheMongodbPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(
            settings['MONGO_HOST'],
            settings['MONGO_PORT']
        )
        self.db = self.client['yiche']
        self.config_collection = self.db['config']
        self.koubei_collection = self.db['koubei']
        self.carname_collection = self.db['carname']
        self.configmap_collection = self.db['configmap']
        self.average_collection = self.db['average']

    def process_item(self, item, spider):
        try:
            if 'serialID' in item.keys():
                self.config_collection.insert(dict(item))
            elif 'carname' in item.keys():
                self.carname_collection.insert(dict(item))
            elif 'serialID_koubei' in item.keys():
                self.koubei_collection.insert(dict(item))
            elif 'average' in item.keys():
                self.average_collection.insert(dict(item))
            else:
                self.configmap_collection.insert(dict(item))
        except Exception as e:
            logger = logging.getLogger('YicheMongodbPipeline')
            logger.error(e)
        return item


# autohome mongodb pipeline
class AutohomeMongodbPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(
            settings['MONGO_HOST'],
            settings['MONGO_PORT']
        )
        self.db = self.client['autohome']
        self.config_collection = self.db['config']
        self.koubei_collection = self.db['koubei']
        self.average_collection = self.db['average']

    def process_item(self, item, spider):
        try:
            if 'seriesitem_id' in item.keys():
                self.koubei_collection.insert(dict(item))
            elif 'average' in item.keys():
                self.average_collection.insert(dict(item))
            else:
                self.config_collection.insert(dict(item))
        except Exception as e:
            logger.error(e)
        return item


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
        self.collection_nofashion = self.db[settings['MONGO_COLLECTION_NOFASHION']]
        self.collection_haibao = self.db[settings['MONGO_COLLECTION_HAIBAO']]
        self.collection_uliaobao = self.db[settings['MONGO_COLLECTION_ULIAOBAO']]

    def process_item(self, item, spider):
        if type(item) == VogueFashionShowItem:
            collection = self.collection_vogue
        elif type(item) == GqFashionShowItem:
            collection = self.collection_gq
        elif type(item) == NoFashionItem:
            collection = self.collection_nofashion
        elif type(item) == HaibaoItem:
            collection = self.collection_haibao
        else:
            collection = self.collection_uliaobao

        try:
            collection.insert(dict(item))
        except Exception as e:
            logger = logging.getLogger('MongodbStorePipeline')
            logger.error(e)
        return item

    def close_spider(self, spider):
        print('close_spider')
        self.client.close()


# 存储到Mongodb - Vogue
class VogueMongodbStorePipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(
            settings['MONGO_HOST'],
            settings['MONGO_PORT']
        )
        self.db = self.client['fashionshow']
        self.collection_vogue = self.db['vogue_t']

    def process_item(self, item, spider):

        try:
            self.collection_vogue.insert(dict(item))
        except Exception as e:
            logger.error(e)
        return item

    def close_spider(self, spider):
        print('close_spider')
        self.client.close()


# 检测图片是否存在
class DuplicatesImagePipeline(object):
    def process_item(self, item, spider):
        if type(item) == VogueFashionShowItem:
            basepath = settings['IMAGES_STORE'] + 'vogue/'
        elif type(item) == GqFashionShowItem:
            basepath = settings['IMAGES_STORE'] + 'gq/'
        elif type(item) == NoFashionItem:
            basepath = settings['IMAGES_STORE'] + 'nofashion/'
        else:
            basepath = settings['IMAGES_STORE'] + 'haibao/'

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
            folder = 'vogueraw/'
        elif url.find('gqimg') != -1:
            folder = 'gq/'
        elif url.find('nofashion') != -1:
            folder = 'nofashion/'
        else:
            folder = 'haibao/'
        return folder + self.md5(url) + '.jpg'

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()


# Adm Pipeline
class AdmImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        request = Request(item['img_url'])
        request.meta['item'] = item
        yield request

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        img = item['_id'] + '.jpg'
        return img

    def item_completed(self, results, item, info):
        img_paths = [x['path'] for ok, x in results if ok]
        if not img_paths:
            raise DropItem('Item contains no images')
        return item


# 存储到Mongodb
class AdmMongoPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(
            settings['MONGO_HOST'],
            settings['MONGO_PORT']
        )
        self.db = self.client['Adm']
        self.collection = self.db['experts']

    def process_item(self, item, spider):
        try:
            self.collection.insert(dict(item))
        except Exception as e:
            logger.error(e)
        return item

    def close_spider(self, spider):
        self.client.close()


# MySQL Pipeline
class AdmMysqlPipeline(object):
    def __init__(self):
        self.connection = MySQLdb.connect(host='192.168.39.25', port=3306, user='root', passwd='7Rgag9o868YigP2E',
                                          db='dataparkcn', charset='utf8')
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        sql = 'insert into experts_imgs (img_md5, img_url, expert_name, expert_info) VALUES ("%s", "%s", "%s", "%s")' % (
            item['_id'], item['img_url'], item['name'], item['intro'])
        print sql
        self.cursor.execute(sql)
        self.connection.commit()

    def close_spider(self, spider):
        self.connection.close()


# # kafka Pipeline
# class KafkaPipeline(object):
#     def __init__(self):
#         self.producer = KafkaProducer(bootstrap_servers=settings['KAFKA_URI'])
#
#     def process_item(self, item, spider):
#         if type(item) == VogueFashionShowItem:
#             topic = settings['TOPIC_VOGUE']
#         elif type(item) == GqFashionShowItem:
#             topic = settings['TOPIC_GQ']
#         else:
#             topic = settings['TOPIC_NOFASHION']
#         item = dict(item)
#         json_item =json.dumps(item)
#         self.producer.send(topic, json_item)
#         self.producer.flush()
# 
#     def close_spider(self, spider):
#         self.producer.close()


# kafka Pipeline
class AutohomeKafkaPipeline(object):
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=settings['KAFKA_URI'])

    def process_item(self, item, spider):
        if item['type'] != 'config':
            if item['type'] == 'purchase_goal':
                topic = settings['TOPIC_AUTOHOME_PURCHASE_GOAL']
            elif item['type'] == 'trouble_rank':
                topic = settings['TOPIC_AUTOHOME_TROUBLE_RANK']
            elif item['type'] == 'trouble_detail':
                topic = settings['TOPIC_AUTOHOME_TROUBLE_DETAIL']
            else:
                topic = settings['TOPIC_AUTOHOME_KOUBEI']
            item = dict(item)
            json_item = json.dumps(item)
            self.producer.send(topic, json_item)
            self.producer.flush()

    # 这里遇到的问题: 一开始从__del__(稀构函数)里面关闭的close,导致的问题,是producer没有写入kafka就关闭了,
    # 正确的关闭应该是从scrapy的关闭函数进行关闭。
    def close_spider(self, spider):
        self.producer.close()


# Autohome_copy Pipeline
class AutohomePipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(
            settings['MONGO_HOST'],
            settings['MONGO_PORT']
        )
        self.db = self.client['autohome_more2']
        self.config_collection = self.db['config']
        self.koubei_collection = self.db['koubei']
        self.purchase_goal_collection = self.db['purchase_goal']
        self.trouble_rank = self.db['trouble_rank']
        self.trouble_detail = self.db['trouble_detail']

    def process_item(self, item, spider):
        try:
            if item['type'] == 'koubei':
                self.koubei_collection.insert(dict(item))
            elif item['type'] == 'purchase_goal':
                self.purchase_goal_collection.insert(dict(item))
            elif item['type'] == 'trouble_rank':
                self.trouble_rank.insert(dict(item))
            elif item['type'] == 'trouble_detail':
                self.trouble_detail.insert(dict(item))
            else:
                self.config_collection.insert(dict(item))
        except Exception as e:
            logger.error(e)
        return item

    def close_spider(self, spider):
        self.client.close()


# WeiboKafka
class WeiboSearchKafkaPipeline(object):
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=settings['KAFKA_URI'])

    def process_item(self, item, spider):
        topic = settings['TOPIC_WEIBO']
        item = dict(item)
        json_item = json.dumps(item)
        self.producer.send(topic, json_item)
        self.producer.flush()


# 这里遇到的问题: 一开始从__del__(稀构函数)里面关闭的close,导致的问题,是producer没有写入kafka就关闭了,
# 正确的关闭应该是从scrapy的关闭函数进行关闭。
def close_spider(self, spider):
    self.producer.close()  # Autohome_


class WeiboSearchMongodbPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(
            settings['MONGO_HOST'],
            settings['MONGO_PORT']
        )
        self.db = self.client['weibosearch']
        self.collection = self.db['content']

    def process_item(self, item, spider):
        try:
            self.collection.insert(dict(item))
        except Exception as e:
            logger.error(e)
        return item

    def close_spider(self, spider):
        self.client.close()
