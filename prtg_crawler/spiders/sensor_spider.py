import json
import re
import scrapy
from scrapy.utils.project import get_project_settings
import redis
from datetime import datetime, timedelta
from urllib.parse import urlparse
from urllib.parse import parse_qs
import pymysql


class SensorSpider(scrapy.Spider):
    name = "sensor"
    iterator = 'iternodes'  # This is actually unnecessary, since it's the default value
    itertag = 'sensortree'
    start_urls = []

    settings = get_project_settings()

    redis = redis.StrictRedis(
        host=settings.get('REDIS_HOST'),
        password=settings.get('REDIS_PASSWORD'),
        port=settings.get('REDIS_PORT'),
        db=settings.get('REDIS_DB_INDEX'),
    )

    # setting MySQL connect
    connect = pymysql.connect(
        host=settings.get('MYSQL_HOST'),
        db=settings.get('MYSQL_DB'),
        user=settings.get('MYSQL_USER'),
        passwd=settings.get('MYSQL_PWD'),
        charset='utf8mb4'
    )

    # 若為當月1號，將上個月的資料複製一份，並新開db
    month_start_day = (datetime.today() - timedelta(days=datetime.now().day - 1))
    last_month = (month_start_day - timedelta(days=1))
    month_start_day = month_start_day.strftime("%Y-%m-%d")
    last_month = last_month.strftime("_%Y_%m")

    today_date = datetime.today().strftime("%Y-%m-%d")
    if month_start_day == today_date:
        cursor = connect.cursor()
        cursor.execute("create table historic" + last_month + " select * from historic")
        cursor.execute("Show tables")
        query = cursor.fetchall()

    time_range = {}
    current_time = datetime.today()
    start_time = (current_time + timedelta(days=-1)).strftime("%Y-%m-%d-00-00-00")
    end_time = (current_time + timedelta(days=-1)).strftime("%Y-%m-%d-23-59-00")

    sensors_menu = redis.get('sensors_menu')
    redis.set('sensors_menu_copy', sensors_menu)
    rows = json.loads(redis.get('sensors_menu_copy'))

    for row in rows:
        URL = 'http://172.31.251.9:8080/api/historicdata.json?id=' + str(row['sensor_id']) + '&avg=0&sdate=' + start_time + '&edate' \
                                                                                                 '=' + end_time + '&usecaption=1&username=' + settings.get('PRTG_USERNAME') + '&passhash=' + settings.get('PRTG_PASSHASH')
        start_urls.append(URL)



    def parse(self, response):
        historics = json.loads(response.text)
        url = response.request.url
        parsed_url = urlparse(url)
        sensor_id = parse_qs(parsed_url.query)['id'][0]

        num = 0
        for historic in historics['histdata']:
            print('Count:', len(historic))
            incomingRefer = 'Incoming_Traffic (speed)'
            outgoingRefer = 'Outgoing_Traffic (speed)'
            historic_item_list = {}
            for idx, name in enumerate(historic):
                if incomingRefer in name or outgoingRefer in name and '(volume)' not in name:

                    if name.find(incomingRefer) != -1:
                        if isinstance(historic[name], str):
                            incoming = historic[name]
                        else:
                            incoming = self.traffic_format(historic[name])
                        incoming_name_list = name.split('_')
                        key = str(num) + '_' + str(incoming_name_list[0].replace(' ', '-')) + '_' + str(sensor_id)

                        if key in historic_item_list:
                            historic_item_list[key]['incoming'] = incoming
                            historic_item_list[key]['raw_incoming'] = incoming
                        else:
                            historic_item_list[key] = {}
                            historic_item_list[key]['sensor_id'] = sensor_id
                            historic_item_list[key]['datetime'] = self.get_date(historic['datetime'])
                            historic_item_list[key]['prefix'] = incoming_name_list[0]
                            historic_item_list[key]['incoming'] = incoming
                            historic_item_list[key]['raw_incoming'] = incoming
                            historic_item_list[key]['outgoing'] = None
                            historic_item_list[key]['raw_outgoing'] = None


                    if name.find(outgoingRefer) != -1:
                        if isinstance(historic[name], str):
                            outgoing = historic[name]
                        else:
                            outgoing = self.traffic_format(historic[name])
                        outgoing_name_list = name.split('_')
                        key = str(num) + '_' + str(outgoing_name_list[0].replace(' ', '-')) + '_' + str(sensor_id)

                        if key in historic_item_list:
                            historic_item_list[key]['outgoing'] = outgoing
                            historic_item_list[key]['raw_outgoing'] = outgoing
                        else:
                            print('not')
                            print('key:'+key)
                            print('name:' + name)
                            print('historic_item:', historic_item_list.keys())
                            historic_item_list[key] = {}
                            historic_item_list[key]['sensor_id'] = sensor_id
                            historic_item_list[key]['datetime'] = self.get_date(historic['datetime'])
                            historic_item_list[key]['prefix'] = outgoing_name_list[0]
                            historic_item_list[key]['incoming'] = None
                            historic_item_list[key]['raw_incoming'] = None
                            historic_item_list[key]['outgoing'] = outgoing
                            historic_item_list[key]['raw_outgoing'] = outgoing

                if idx+1 == len(historic):
                    for historic_item in historic_item_list:
                        cidr_regex = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$'
                        if re.match(cidr_regex, str(historic_item_list[historic_item]['prefix'])):
                            print(historic_item_list[historic_item])
                            print("------------------------------")
                            yield historic_item_list[historic_item]

                    print(historic_item_list)
                    print("------------------------------")

            num += 1

    def get_date(self, row_datetime):
        datetime_str_temp = str(row_datetime).split(' ')
        datetime_str = str(datetime_str_temp[1] + datetime_str_temp[2]).split(':')

        hours_mapping_dict = {
            '下午01': '13', '下午02': '14', '下午03': '15', '下午04': '16', '下午05': '17', '下午06': '18', '下午07': '19', '下午08': '20',
            '下午09': '21', '下午10': '22', '下午11': '23', '下午12': '12', '上午01': '01', '上午02': '02', '上午03': '03', '上午04': '04',
            '上午05': '05', '上午06': '06', '上午07': '07', '上午08': '08', '上午09': '09', '上午10': '10', '上午11': '11', '上午12': '00'
        }

        datetime_str = str(datetime_str_temp[0]) + ' ' + str(hours_mapping_dict[str(datetime_str[0])]) + ':' + str(datetime_str[1]) + ':' + str(datetime_str[2])
        datetime_str = datetime_str.replace('/', '-')
        return datetime_str

    def traffic_format(self, data):
        return float(data) * 8 if float(data) > 0 and float(data) != '' else float(data)
