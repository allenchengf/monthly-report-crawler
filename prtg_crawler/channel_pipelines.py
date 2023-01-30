from .model import Base, engine, loadSession
from twisted.enterprise import adbapi
from .model import channel
import logging
from prtg_crawler.items import ChannelItem

class ChannelCrawlerPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_crawler(cls, prtg_crawler):
        dbparams = {
            'host': prtg_crawler.settings['MYSQL_HOST'],
            'user': prtg_crawler.settings['MYSQL_USER'],
            'passwd': prtg_crawler.settings['MYSQL_PWD'],
            'db': prtg_crawler.settings['MYSQL_DB'],
            'port': prtg_crawler.settings['MYSQL_PORT'],
            'charset': prtg_crawler.settings['MYSQL_CHARSET']
        }
        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        if isinstance(item, ChannelItem):
            # 入庫
            query = self.dbpool.runInteraction(
                self.insert_db,
                item
            )
            query.addErrback(
                self.insert_err,
                item
            )
        return item

    def insert_err(self, failure, item):
        print(failure, 'fail')  # , item)

    def open_spider(self, spider):
        logging.info('start channels crawler.')
        truncate_sql = 'truncate table channels'
        self.dbpool.runOperation(truncate_sql)
        print('truncate channels table.')

    def insert_db(self, cursor, item):
        insert_sql = """
                        insert into channels( 
                        sensor_id, 
                        name, 
                        lastvalue)
                        values (%s, %s, %s)
                        """
        params = (item['sensor_id'],
                  item['name'],
                  item['lastvalue'])
        cursor.execute(insert_sql, params)

    def close_spider(self, spider):
        self.dbpool.close()
