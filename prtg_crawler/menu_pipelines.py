import json
import logging
import time

import pymysql
import redis
from scrapy.utils.project import get_project_settings
from collections import defaultdict


class MenuPipeline(object):
    def __init__(self, ):
        settings = get_project_settings()
        self.redis = redis.StrictRedis(
            host=settings.get('REDIS_HOST'),
            password=settings.get('REDIS_PASSWORD'),
            port=settings.get('REDIS_PORT'),
            db=settings.get('REDIS_DB_INDEX'),
        )

        # setting MySQL connect
        self.connect = pymysql.connect(
            host=settings.get('MYSQL_HOST'),
            db=settings.get('MYSQL_DB'),
            user=settings.get('MYSQL_USER'),
            passwd=settings.get('MYSQL_PWD'),
            charset='utf8mb4'
        )
        self.cursor = self.connect.cursor()

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        print('start generate prefixes menu')
        time.sleep(30)
        self.generate_prefixes_menu()
        self.cursor.close()
        self.connect.close()

    def generate_prefixes_menu(self):
        print('start generate prefixes menu')
        try:
            self.cursor.execute("select distinct sensor_id,prefix from historic order by sensor_id asc")
            rows = self.cursor.fetchall()
            multi_dict = defaultdict(list)
            for k, v in rows:
                multi_dict[k].append(v)
            prefixes_menu_json_str = json.dumps(multi_dict)
            print(prefixes_menu_json_str)
            self.redis.set('prefixes_menu', prefixes_menu_json_str)
        except Exception as err:
            print('fail', err)
        finally:
            print('close generate prefixes menu')
