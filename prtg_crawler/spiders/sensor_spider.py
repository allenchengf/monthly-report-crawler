import json
import re
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
                        historic_item = {key: {'sensor_id': sensor_id,
                                               'datetime': historic['datetime'],
                                               'prefix': incoming_name_list[0],
                                               'incoming': incoming,
                                               'raw_incoming': incoming
                                               }
                                         }

                    if name.find(outgoingRefer) != -1:
                        if isinstance(historic[name], str):
                            outgoing = historic[name]
                        else:
                            outgoing = int(float(historic[name])) * 8 if int(float(historic[name])) > 0 & int(float(
                                historic[name])) != '' else int(float(historic[name]))
                        outgoing_name_list = name.split('_')
                        key = str(num) + '_' + str(outgoing_name_list[0]) + '_' + str(sensor_id) + '_outgoing'
                        historic_item = {key: {'sensor_id': sensor_id,
                                               'datetime': historic['datetime'],
                                               'prefix': outgoing_name_list[0],
                                               'outgoing': outgoing,
                                               'raw_outgoing': outgoing
                                               }
                                         }
                        # historic_item[key]['outgoing'] = outgoing
                        # historic_item[key]['raw_outgoing'] = outgoing

                        print(historic_item)
                        print("------------------------------")
            num += 1
