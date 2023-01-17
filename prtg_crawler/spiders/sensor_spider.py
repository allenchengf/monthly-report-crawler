from datetime import datetime
import json
import re
import time
import calendar
import scrapy


class SensorSpider(scrapy.Spider):
    name = "sensor"
    start_urls = ['http://172.31.251.9:8080/api/table.xml?content=sensortree&passhash=3168990700&username=ict.monitor'
                  '&columns=sensor']
    iterator = 'iternodes'  # This is actually unnecessary, since it's the default value
    itertag = 'sensortree'

    def parse(self, response):
        sensors = response.xpath("//sensortree/nodes/group//sensor").getall()
        sflow_sensortype_refor = "<sensortype>sFlow (Custom)</sensortype>"
        ipfix_sensortype_refor = "<sensortype>IPFIX (Custom)</sensortype>"
        sensor_factory_sensortype_refor = "<sensortype>Sensor Factory</sensortype>"
        for ids, sensor in enumerate(sensors):
            if sflow_sensortype_refor in sensor or ipfix_sensortype_refor in sensor or sensor_factory_sensortype_refor in sensor:
                # print(sensor)
                item = {
                    'ids': ids,
                    "id": re.findall("(?:<id.*?>)(.*?)(?:<\\/id>)", sensor),
                    "url": re.findall("(?:<url.*?>)(.*?)(?:<\\/url>)", sensor),
                    "tags": re.findall("(?:<tags.*?>)(.*?)(?:<\\/tags>)", sensor),
                    "interval": re.findall("(?:<interval.*?>)(.*?)(?:<\\/interval>)", sensor),
                    "status": re.findall("(?:<status.*?>)(.*?)(?:<\\/status>)", sensor),
                    "active": re.findall("(?:<active.*?>)(.*?)(?:<\\/active>)", sensor),
                }
                item['channel_url'] = 'http://172.31.251.9:8080/api/table.json?content=channels&output=json&columns=name,' \
                                      'lastvalue_&id=' + str(item["id"]).replace("['", "").replace("']",
                                                                                                   "") + '&username=ict.monitor&passhash=3168990700'

                # print(item)
                yield scrapy.Request(item['channel_url'], meta={'item': item}, callback=self.channel_parse)
                # yield item

    def channel_parse(self, response):
        item = response.meta['item']
        channels = json.loads(response.text)
        for channel in channels['channels']:
            sensor_id = str(item['id']).replace("['", "").replace("']", "")
            name = channel['name']
            del channel['name']
            channel_item = {
                "sensor_id": sensor_id,
                "name": name,
                "value": json.dumps(channel)
            }
            # print(channel_item)
            # print("----------------")
            historic_url = 'http://172.31.251.9:8080/api/historicdata.json?id=' + sensor_id + '&avg=0&sdate=2023-01-15-00-00-00&edate' \
                                                                                              '=2023-01-15-23-59-00&usecaption=1&username=ict.monitor&passhash=3168990700'

            yield scrapy.Request(historic_url, meta={'item': item, 'channel_item': channel_item},
                                 callback=self.historic_parse)

    def historic_parse(self, response):
        item = response.meta['item']
        channel_item = response.meta['channel_item']
        historics = json.loads(response.text)

        num = 0
        for historic in historics['histdata']:
            sensor_id = str(item['id']).replace("['", "").replace("']", "")

            incomingRefer = 'Incoming_Traffic (speed)'
            outgoingRefer = 'Outgoing_Traffic (speed)'

            historic_item = {}
            for idx, name in enumerate(historic):
                if incomingRefer or outgoingRefer in name:

                    if name.find(incomingRefer) != -1:
                        if isinstance(historic[name], str):
                            incoming = historic[name]
                        else:
                            incoming = int(float(historic[name])) * 8 if int(float(historic[name])) > 0 & int(float(
                                historic[name])) != '' else int(float(historic[name]))
                        incoming_name_list = name.split('_')
                        key = str(num) + '_' + str(incoming_name_list[0].replace(' ', '-')) + '_' + str(sensor_id)

                        if key not in historic_item.keys():
                            historic_item = {key: {}}

                        historic_item[key]['sensor_id'] = sensor_id
                        historic_item[key]['datetime'] = self.get_date(historic['datetime'])
                        historic_item[key]['prefix'] = incoming_name_list[0]
                        historic_item[key]['incoming'] = incoming
                        historic_item[key]['raw_incoming'] = incoming

                    if name.find(outgoingRefer) != -1:
                        if isinstance(historic[name], str):
                            outgoing = historic[name]
                        else:
                            outgoing = int(float(historic[name])) * 8 if int(float(historic[name])) > 0 & int(float(
                                historic[name])) != '' else int(float(historic[name]))
                        outgoing_name_list = name.split('_')
                        key = str(num) + '_' + str(outgoing_name_list[0].replace(' ', '-')) + '_' + str(sensor_id)

                        if key not in historic_item.keys():
                            historic_item = {key: {}}

                        historic_item[key]['sensor_id'] = sensor_id
                        historic_item[key]['datetime'] = self.get_date(historic['datetime'])
                        historic_item[key]['prefix'] = outgoing_name_list[0]
                        historic_item[key]['outgoing'] = outgoing
                        historic_item[key]['raw_outgoing'] = outgoing

                        print(historic_item)
                        print("------------------------------")
            num += 1

    def get_date(self, row_datetime):
        datetime_str_temp = str(row_datetime).split(' ')
        datetime_str = str(datetime_str_temp[1] + datetime_str_temp[2]).split(':')

        hours_mapping_dict = {
            '下午01': '13', '下午02': '14', '下午03': '15', '下午04': '16', '下午05': '17', '下午06': '18', '下午07': '19', '下午08': '20',
            '下午09': '21', '下午10': '22', '下午11': '23', '下午12': '24', '上午01': '01', '上午02': '02', '上午03': '03', '上午04': '04',
            '上午05': '05', '上午06': '06', '上午07': '07', '上午08': '08', '上午09': '09', '上午10': '10', '上午11': '11', '上午12': '00'
        }

        datetime_str = str(datetime_str_temp[0]) + ' ' + str(hours_mapping_dict[str(datetime_str[0])]) + ':' + str(datetime_str[1]) + ':' + str(datetime_str[2])
        datetime_str = datetime_str.replace('/', '-')
        return datetime_str
