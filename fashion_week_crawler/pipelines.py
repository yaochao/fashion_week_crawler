# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import MySQLdb.cursors
from scrapy.http import Request
from twisted.enterprise import adbapi
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import os

# BASE_PATH
BASE_PATH = '/data/datapark/yaochao/download/vogue/'
# BASE_PATH = '/Users/yaochao/Desktop/vogue/'


# 示例 Pipeline
class FashionWeekCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


# 存储信息到 MySQL 的 Pipeline, 优先级:1
class MySQLStoreVoguePipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    # 扩展的方法
    @classmethod
    def from_crawler(cls, crawler):
        dbargs = dict(
            host=crawler.settings['MYSQL_HOST'],
            db=crawler.settings['MYSQL_DBNAME'],
            user=crawler.settings['MYSQL_USER'],
            passwd=crawler.settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.dbpool.close()

    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

    # 更新或者写入
    def _do_upinsert(self, cursor, item, spider):
        cursor.execute('select * from vogue where md5 = "%s"', (item['md5'],))
        ret = cursor.fetchone()
        if ret:
            print 'item already exists in db'
        else:
            cursor.execute('insert into vogue(name, brand, md5, url, comment, city, year, season, type) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)', (item['name'], item['brand'], item['md5'], item['url'], item['comment'], item['city'], item['year'], item['season'], item['type']))

    #错误处理
    def _handle_error(self, failue, item, spider):
        with open('pipelines_error.txt', 'a') as f:
            f.write('pipeline failue %s\n url:%s\n' % (failue, item['url']))



# 检测图片是否存在的Pipeline
class DuplicatesPipeline(object):

    # 做为Pipeline, scrapy会自动调用此方法
    def process_item(self, item, spider):
        filename = item['md5'] + '.jpg'
        filepath = BASE_PATH + filename
        print 'filepath', filepath
        if os.path.exists(filepath):
            raise DropItem("Image already exists")
        else:
            return item


# 保存图片 Pipeline ,优先级:300
class SaveImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        yield Request(item['url'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        filename = item['md5'] + '.jpg'
        filepath = BASE_PATH + filename
        os.rename(BASE_PATH + image_paths[0], filepath) # 给图片重命名
        return item