from .model import Base,engine, loadSession
from .model import Sensors
import logging


class PrtgCrawlerPipeline:
    Base.metadata.create_all(engine)

    def __init__(self):
        session = loadSession()
        try:
            session.execute('TRUNCATE TABLE sensors')
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(e)

    def process_item(self, item, spider):
        try:
            a = Sensors.Sensor(
                name=item['name'],
                sensor_id=item['sensor_id'],
                url=item['url'],
                tags=item['tags'],
                interval=item['interval'],
                status=item['status'],
                active=item['active']
            )
            session = loadSession()
            session.add(a)
            session.commit()

        except Exception as e:
            logging.info(e)
