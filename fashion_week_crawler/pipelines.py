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
from scrapy.utils.project import get_project_settings

# settings.py
settings = get_project_settings()


# # 存储信息到 MySQL 的 Pipeline
# class MySQLStoreVoguePipeline(object):
#     def __init__(self):
#         dbargs = dict(
#             host=settings['MYSQL_HOST'],
#             db=settings['MYSQL_DBNAME'],
#             user=settings['MYSQL_USER'],
#             passwd=settings['MYSQL_PASSWD'],
#             charset='utf8',
#             cursorclass=MySQLdb.cursors.DictCursor,
#             use_unicode=True,
#         )
#         self.dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
#
#     def open_spider(self, spider):
#         pass
#
#     def close_spider(self, spider):
#         self.dbpool.close()
#
#     def process_item(self, item, spider):
#         d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
#         d.addErrback(self._handle_error, item, spider)
#         d.addBoth(lambda _: item)
#         return d
#
#     # 更新或者写入
#     def _do_upinsert(self, cursor, item, spider):
#         cursor.execute('select * from vogue where md5 = "%s"', (item['md5'],))  # redis
#         ret = cursor.fetchone()
#         if ret:
#             print 'item already exists in db'
#         else:
#             cursor.execute(
#                 'insert into vogue(name, brand, md5, url, comment, city, year, season, type) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
#                 (item['name'], item['brand'], item['md5'], item['image_urls'][0], item['comment'], item['city'],
#                  item['year'],
#                  item['season'], item['type']))
#
#     # 错误处理
#     def _handle_error(self, failue, item, spider):
#         with open('pipelines_error.txt', 'a') as f:
#             f.write('pipeline failue %s\n url:%s\n' % (failue, item['url']))


# 存储到Mongodb
class MongodbStorePipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(
            settings['MONGO_HOST'],
            settings['MONGO_PORT']
        )
        self.db = self.client[settings['MONGO_DB']]
        self.collection = self.db[settings['MONGO_COLLECTION']]

    def process_item(self, item, spider):
        try:
            self.collection.insert(dict(item))
        except Exception as e:
            print 'error---%s' % e
        return item

    def close_spider(self, spider):
        self.client.close()


# 检测图片是否存在
class DuplicatesImagePipeline(object):
    # 做为Pipeline, scrapy会自动调用此方法
    def process_item(self, item, spider):
        filename = item['_id'] + '.jpg'
        filepath = settings['IMAGES_STORE'] + filename
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
        return self.md5(url) + '.jpg'

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
