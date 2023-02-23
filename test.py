# from core.consumer import MessageConsumer
# from core.producer import MessageProducer

# topic = "mytopic"
# group_id = "my_group"
# producer = MessageProducer(broker="localhost:9092", topic=topic)
# message = {'name':'abc', 'email':'abc@example.com'}
# producer.send_msg(message)


# consumer = MessageConsumer(topic=topic, group_id=group_id)
# consumer._fetch()
# print("done")

# from core.task import TaskManager
# task1 = {
#     'task_id': 1,
#     'script': 'run.bat',
#     'target': '',
#     'params': ''
# }
# print(TaskManager.start_task(task1))

# from core.consumer import MessageConsumer

# consumer = MessageConsumer(topic="WX-C-001GN", group_id="WX-C-001GN")

# consumer._poll()

from datetime import datetime, timezone
tz = datetime.now(timezone.utc).astimezone().tzinfo

now = datetime.now()
print("now: ", now)
utc_now = datetime.utcnow()
print("utcnow: ", utc_now)

conv = datetime.utcfromtimestamp(now.timestamp())

print("conv: ", conv)

print("timestamp:", now.timestamp())