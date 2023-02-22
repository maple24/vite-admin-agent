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

from core.task import TaskManager
task1 = {
    'task_id': 1,
    'script': 'run.bat',
    'target': '',
    'params': ''
}
print(TaskManager.start_task(task1))