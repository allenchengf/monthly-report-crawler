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
        print('start generate menu')
        time.sleep(10)
        self.generate_sensors_menu()
        self.generate_channels_menu()
        self.cursor.close()
        self.connect.close()

    def generate_sensors_menu(self):
        print('start generate sensors menu')
        try:
            self.cursor.execute("select id, name, sensor_id from sensors")
            rows = self.cursor.fetchall()
            sensors_menu = []
            for row in rows:
                menu_item = {}
                for index in range(len(self.cursor.description)):
                    key = self.cursor.description[index][0]
                    menu_item[key] = row[index]
                print(menu_item)
                sensors_menu.append(menu_item)
            sensors_menu_json_str = json.dumps(sensors_menu)
            print(sensors_menu_json_str)
            self.redis.set('sensors_menu', sensors_menu_json_str)
        except Exception as err:
            print('fail', err)
        finally:
            print('close generate sensors menu')

    def generate_channels_menu(self):
        print('start generate channels menu')
        try:
            self.cursor.execute("select sensor_id, name from channels")
            rows = self.cursor.fetchall()
            multi_dict = defaultdict(list)
            for k, v in rows:
                multi_dict[k].append(v)
            channels_menu_json_str = json.dumps(multi_dict)
            print(channels_menu_json_str)
            self.redis.set('channels_menu', channels_menu_json_str)
        except Exception as err:
            print('fail', err)
        finally:
            print('close generate channels menu')
