import json
import re
import time
import calendar
import scrapy
from scrapy.utils.project import get_project_settings
import redis
from datetime import datetime, timedelta


class SensorSpider(scrapy.Spider):
    settings = get_project_settings()

    name = "sensor"
    start_urls = ['http://172.31.251.9:8080/api/table.xml?content=sensortree&passhash=' + settings.get('PRTG_PASSHASH') + '&username=' + settings.get('PRTG_USERNAME') +
                  '&columns=sensor']
    iterator = 'iternodes'  # This is actually unnecessary, since it's the default value
    itertag = 'sensortree'

    def __init__(self):
        settings = get_project_settings()
        self.redis = redis.StrictRedis(
            host=settings.get('REDIS_HOST'),
            password=settings.get('REDIS_PASSWORD'),
            port=settings.get('REDIS_PORT'),
            db=settings.get('REDIS_DB_INDEX'),
        )


    def parse(self, response):
        sensors = response.xpath("//sensortree/nodes/group//sensor").getall()
        sflow_sensortype_refor = "<sensortype>sFlow (Custom)</sensortype>"
        ipfix_sensortype_refor = "<sensortype>IPFIX (Custom)</sensortype>"
        # sensor_factory_sensortype_refor = "<sensortype>Sensor Factory</sensortype>"
        for ids, sensor in enumerate(sensors):
            # if sflow_sensortype_refor in sensor or ipfix_sensortype_refor in sensor or sensor_factory_sensortype_refor in sensor:
            if sflow_sensortype_refor in sensor or ipfix_sensortype_refor in sensor:
                # print(sensor)
                Sensor_item = {
                    'ids': ids,
                    'name': re.findall("(?:<name.*?>)(.*?)(?:<\\/name>)", sensor),
                    "sensor_id": re.findall("(?:<id.*?>)(.*?)(?:<\\/id>)", sensor),
                    "url": re.findall("(?:<url.*?>)(.*?)(?:<\\/url>)", sensor),
                    "tags": re.findall("(?:<tags.*?>)(.*?)(?:<\\/tags>)", sensor),
                    "status": re.findall("(?:<status.*?>)(.*?)(?:<\\/status>)", sensor),
                    "active": re.findall("(?:<active.*?>)(.*?)(?:<\\/active>)", sensor),
                }
                Sensor_item['channel_url'] = 'http://172.31.251.9:8080/api/table.json?content=channels&output=json&columns=name,' \
                                      'lastvalue_&id=' + str(Sensor_item["sensor_id"]).replace("['", "").replace("']",
                                                                                                   "") + '&username='+ self.settings.get('PRTG_USERNAME') + '&passhash=' + self.settings.get('PRTG_PASSHASH')

                # print(Sensor_item)
                yield scrapy.Request(Sensor_item['channel_url'], meta={'item': Sensor_item}, callback=self.channel_parse)
                yield Sensor_item

    def channel_parse(self, response):
        time_range = self.set_time_range()
        item = response.meta['item']
        channels = json.loads(response.text)
        for channel in channels['channels']:
            sensor_id = str(item['sensor_id']).replace("['", "").replace("']", "")
            name = channel['name']
            del channel['name']

            cidr_regex = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))')
            if cidr_regex.search(name):
                channel_item = {
                    "sensor_id": sensor_id,
                    "name": name,
                    "lastvalue": json.dumps(channel)
                }
                historic_url = 'http://172.31.251.9:8080/api/historicdata.json?id=' + sensor_id + '&avg=0&sdate=' + time_range['start_time'] + '&edate' \
                                                                                                 '=' + time_range['end_time'] + '&usecaption=1&username=' + self.settings.get('PRTG_USERNAME') + '&passhash=' + self.settings.get('PRTG_PASSHASH')

                yield scrapy.Request(historic_url, meta={'item': item}, callback=self.historic_parse)
                yield channel_item

    def historic_parse(self, response):
        item = response.meta['item']
        historics = json.loads(response.text)

        num = 0
        for historic in historics['histdata']:
            print('Count:', len(historic))
            sensor_id = str(item['sensor_id']).replace("['", "").replace("']", "")
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

    def set_time_range(self):
        time_range = {}
        current_time = datetime.today()
        time_range['start_time'] = (current_time + timedelta(days=-1)).strftime("%Y-%m-%d-00-00-00")
        time_range['end_time'] = (current_time + timedelta(days=-1)).strftime("%Y-%m-%d-23-59-00")

        return time_range
