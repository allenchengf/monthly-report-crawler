import re
import scrapy
from sensordata.items import PrtgCrawlerItem

class PRTGSpider(scrapy.Spider):
    name = "sensor"
    start_urls = ['http://172.31.251.9:8080/api/table.xml?content=sensortree&passhash=3168990700&username=ict.monitor'
                  '&columns=sensor']
    iterator = 'iternodes'  # This is actually unnecessary, since it's the default value
    itertag = 'sensortree'

    def parse(self, selector):
        sensors = selector.xpath("//sensortree/nodes/group//sensor").getall()
        for sensor in sensors:
            item = {
                "id": re.findall("(?:<id.*?>)(.*?)(?:<\\/id>)", sensor),
                "url": re.findall("(?:<url.*?>)(.*?)(?:<\\/url>)", sensor),
                "tags": re.findall("(?:<tags.*?>)(.*?)(?:<\\/tags>)", sensor),
                "interval": re.findall("(?:<interval.*?>)(.*?)(?:<\\/interval>)", sensor),
                "status": re.findall("(?:<status.*?>)(.*?)(?:<\\/status>)", sensor),
                "active": re.findall("(?:<active.*?>)(.*?)(?:<\\/active>)", sensor)
            }

            yield item
            print("----------------------")
