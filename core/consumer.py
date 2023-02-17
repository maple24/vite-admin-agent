'''
consume message from kafka
'''
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kafka import KafkaConsumer
import json
import threading
from core.config import cfg
from loguru import logger


class MessageConsumer(threading.Thread):
    broker = cfg.get('kafka').get('servers')
    consumer = None
    
    def __init__(self, topic: list, group_id: str=None, callback=None, client_id='', auto_offset_reset='earliest'):
        super().__init__()
        self.topic = topic
        self.callback = callback
        self.group_id = group_id
        self.consumer = KafkaConsumer(bootstrap_servers=self.broker,
                            group_id = group_id,
                            # consumer_timeout_ms = 1000,
                            auto_offset_reset = auto_offset_reset,
                            enable_auto_commit = False,
                            client_id = client_id, # agent hostname
                            api_version = (0, 10),
                        )
        
    def run(self):
        self._subscribe(self.topic)
        logger.success(f"Kafka consumer subscribed with {self.topic}.")
        for message in self.consumer:
            self._print_message(message)
            if self.group_id: self.consumer.commit()
            key = json.loads(message.key.decode('utf-8'))
            value = json.loads(message.value.decode('utf-8'))
            if self.callback:
                self.callback(key, value)
        logger.error("Kafka consumer disconnected!")

    
    def _subscribe(self, topic):
        '''
        topic can be regrex, eg. ^awesome.*
        '''
        self.consumer.subscribe(topic)
    
    # for note/debug only
    def _fetch(self):
        '''
        fetch all messages from consumer
        '''
        self._subscribe(self.topic)
        for message in self.consumer:
            self._print_message(message)
            if self.group_id: self.consumer.commit()
    
    # for note/debug only
    def _poll(self):
        '''
        poll message from consumer, similar to _fetch method
        '''
        self._subscribe(self.topic)
        while True:
            logger.debug('polling...')
            records = self.consumer.poll(timeout_ms=1000)
            for _, consumer_records in records.items():
                # Parse records
                for consumer_record in consumer_records:
                    logger.debug(str(consumer_record.value.decode('utf-8')))
                continue
    
    # for note/debug only
    def _assign(self, partition: int):
        '''
        read specified partition and every position
        auto_offset should be closed
        '''
        from kafka import TopicPartition
        partition = TopicPartition(topic=self.topic, partition=partition)
        self.consumer.assign([partition])
        for msg in self.consumer:
            logger.debug(self.consumer.position(partition))
            self._print_message(msg)

    # for note/debug only
    def _seek(self, partition: int, offset: int):
        '''
        seek specified position
        auto_offset should be closed
        '''
        from kafka import TopicPartition
        self.consumer.partitions_for_topic(self.topic)
        partition = TopicPartition(topic=self.topic, partition=partition)
        self.consumer.seek(partition=partition, offset=offset)
        for message in self.consumer:
            self._print_message(message)
    
    # for note/debug only
    def _seek_to_beginning(self, partition):
        '''
        seek to beginning, works the same as auto_offset to `earliest`
        '''
        from kafka import TopicPartition
        logger.debug(self.consumer.partitions_for_topic(self.topic)) # check topic
        partition = TopicPartition(topic=self.topic, partition=partition)
        self.consumer.assign([partition])
        self.consumer.seek_to_beginning()
        for message in self.consumer:
            self._print_message(message)

    def _print_message(self, message):
        logger.debug(f"Retrieved message>> {message.topic}:{message.partition}:{message.offset}: key={json.loads(message.key.decode('utf-8'))} value={json.loads(message.value.decode('utf-8'))}")


if __name__ == '__main__':
    topic = "mytopic"
    group_id = "my_group"
    consumer = MessageConsumer(topic=topic, group_id=group_id)
    # consumer._seek_to_beginning(partition=1)
    consumer._fetch()
    print("done")