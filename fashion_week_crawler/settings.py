# -*- coding: utf-8 -*-

# Scrapy settings for fashion_week_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'fashion_week_crawler'

SPIDER_MODULES = ['fashion_week_crawler.spiders']
NEWSPIDER_MODULE = 'fashion_week_crawler.spiders'

# JSONRPC(原来的webservice,已经单独分离开了:https://github.com/scrapy-plugins/scrapy-jsonrpc)
JSONRPC_ENABLED = True
JSONRPC_HOST = '127.0.0.1'
JSONRPC_PORT = [6080, 7030]

# Logging
# LOG_LEVEL = 'ERROR'
# LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
# LOG_FILE = 'scrapy.log'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'fashion_week_crawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

# start MySQL database configure setting
# MYSQL_HOST = '127.0.0.1'
# MYSQL_DBNAME = 'fashionshow'
# MYSQL_USER = 'root'
# MYSQL_PASSWD = ''
# MYSQL_PASSWD = '7Rgag9o868YigP2E'
# MYSQL_PASSWD = 'toor'
# end of MySQL database configure setting

# Mongodb database configure setting
MONGO_HOST = '127.0.0.1'
# MONGO_HOST = '192.168.39.26'
MONGO_PORT = 27017
MONGO_DB = 'fashionshow'
MONGO_COLLECTION_VOGUE = 'vogue'
MONGO_COLLECTION_GQ = 'gq'
MONGO_COLLECTION_NOFASHION = 'nofashion'
MONGO_COLLECTION_HAIBAO = 'haibao'
MONGO_COLLECTION_ULIAOBAO = 'uliaobao'

# Kafka
KAFKA_URI = '192.168.31.6:9092'
TOPIC_VOGUE = 'scrapy_vogue'
TOPIC_GQ = 'scrapy_gq'
TOPIC_NOFASHION = 'scrapy_nofashion2'
TOPIC_HAIBAO = 'scrapy_haibao'
TOPIC_AUTOHOME_KOUBEI = 'autohome_koubei'
TOPIC_AUTOHOME_PURCHASE_GOAL = 'autohome_purchase_goal'
TOPIC_AUTOHOME_TROUBLE_RANK = 'autohome_trouble_rank'
TOPIC_AUTOHOME_TROUBLE_DETAIL = 'autohome_trouble_detail'
TOPIC_WEIBO = 'weibo_content2'


# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY =
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'fashion_week_crawler.middlewares.MyCustomSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'fashion_week_crawler.misc.middlewares.UserAgentMiddleware': 400,
}

DOWNLOAD_TIMEOUT = 20
ROBOTSTXT_OBEY = False
SCHEDULER = 'scrapy.core.scheduler.Scheduler'
STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'
STATS_DUMP = True

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
   # 'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy_jsonrpc.webservice.WebService': 500,
}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'fashion_week_crawler.pipelines.MongodbStorePipeline': 100,
    'fashion_week_crawler.pipelines.DuplicatesImagePipeline': 200,
    'fashion_week_crawler.pipelines.SaveImagesPipeline': 300,
    # 'fashion_week_crawler.pipelines.KafkaPipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# save file to path:

# 注意这里, 使用scrapy自带的ImagesPipeline的默认存储路径是settings.py里面的 IMAGES_STORE 对应的值
IMAGES_STORE = '/Users/yaochao/Desktop/fashionshow/'
# IMAGES_STORE = '/data/datapark/yaochao/download/'
