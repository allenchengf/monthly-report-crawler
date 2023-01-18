from .model import Base, engine, loadSession
from .model import channel
import logging


class ChannelCrawlerPipeline:
    Base.metadata.create_all(engine)

    def __init__(self):
        session = loadSession()
        try:
            session.execute('TRUNCATE TABLE channels')
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(e)

    def process_item(self, item, spider):
        try:
            channel_item = channel.Channel(
                name=item['name'],
                sensor_id=item['sensor_id'],
                lastvalue=item['lastvalue']
            )
            session = loadSession()
            session.add(channel_item)
            session.commit()

        except Exception as e:
            logging.info(e)

        return item
