from .model import Base, engine, loadSession
from .model import historic
import logging


class HistoricCrawlerPipeline:
    Base.metadata.create_all(engine)

    def process_item(self, item, spider):
        try:
            historic_item = historic.Historic(
                sensor_id=item['sensor_id'],
                channel_name=item['channel_name'],
                prefix=item['prefix'],
                incoming=item['incoming'],
                outgoing=item['outgoing'],
                raw_incoming=item['raw_incoming'],
                raw_outgoing=item['raw_outgoing'],
                datetime=item['datetime']
            )
            session = loadSession()
            session.add(historic_item)
            session.commit()

        except Exception as e:
            logging.error(e)

        return item
