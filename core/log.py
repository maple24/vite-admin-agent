import json
from lib.decorators import Singleton
from lib.utils import get_host_name
from lib.message import LogMessage
from queue import Queue
import ast


@Singleton
class LoggerManager:

    def __init__(self, queue: Queue):
        self.queue = queue
        self.hostname = get_host_name()

    def remote_logger(self, message: str):
        '''
        send logs to websockets queue
        ast.literal_eval: parese message, convert string dictionary to dictionary
        task logs have task id
        '''
        raw = message.record.get("message")
        try:
            raw = ast.literal_eval(raw)
        except:
            pass
        if isinstance(raw, dict): 
            task_id = raw.get("task_id")
            content = raw.get("content")
            data = LogMessage.trace(task_id=task_id, content=content.strip())
        else:
            data = LogMessage.trace(hostname=self.hostname, content=message.strip())
        self.queue.put(json.dumps(data))
