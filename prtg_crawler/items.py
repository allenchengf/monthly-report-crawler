import scrapy


class SensorItem(scrapy.Item):
    name = scrapy.Field()
    sensor_id = scrapy.Field()
    url = scrapy.Field()
    tags = scrapy.Field()
    interval = scrapy.Field()
    status = scrapy.Field()
    active = scrapy.Field()


class ChannelItem(scrapy.Item):
    sensor_id = scrapy.Field()
    name = scrapy.Field()
    lastvalue = scrapy.Field()


class HistoricItem(scrapy.Item):
    sensor_id = scrapy.Field()
    channel_name = scrapy.Field()
    datetime = scrapy.Field()
    prefix = scrapy.Field()
    incoming = scrapy.Field()
    raw_incoming = scrapy.Field()
    outgoing = scrapy.Field()
    raw_outgoing = scrapy.Field()
