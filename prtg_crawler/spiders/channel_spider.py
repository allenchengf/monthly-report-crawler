import scrapy


class ChannelSpider(scrapy.Spider):
    name = "channel"

    def __init__(self, sensor=None, *args, **kwargs):
        super(ChannelSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'http://172.31.251.9:8080/api/table.json?content=channels&output=json&columns=name,'
                           f'lastvalue_&id={sensor}&username=ict.monitor&passhash=3168990700']

    def parse(self, response):
        channels = response.xpath("//sensortree/nodes/group//sensor").getall()
        print(channels)
