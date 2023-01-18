import scrapy


class SensorItem(scrapy.Item):
    name = scrapy.Field()
    sensor_id = scrapy.Field()
    url = scrapy.Field()
    tags = scrapy.Field()
    interval = scrapy.Field()
    status = scrapy.Field()
    active = scrapy.Field()

