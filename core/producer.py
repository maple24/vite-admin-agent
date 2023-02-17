from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
from loguru import logger


class MessageProducer:
    broker = ""
    producer = None

    def __init__(self, broker, topic):
        self.broker = broker
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=self.broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: json.dumps(k).encode('utf-8'),
            acks='all',
            retries = 3)


    def send_msg(self, message):
        logger.debug("sending message...")
        try:
            future = self.producer.send(self.topic, message)
            self.producer.flush()
            future.get(timeout=60)
            logger.debug("message sent successfully...")
            return {'status_code':200, 'error':None}
        except KafkaError as e:
            raise e


if __name__ == '__main__':
    broker = 'localhost:9092'
    topic = 'test-topic'
    message_producer = MessageProducer(broker, topic)

    data = {'name':'abc', 'email':'abc@example.com'}
    resp = message_producer.send_msg(data)
    print(resp)