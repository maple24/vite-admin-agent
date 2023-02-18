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
        data = LogMessage.trace(hostname=self.hostname, content=message.strip())
        try: # if message is not able to convert to dict, send it directly
            raw = ast.literal_eval(message.record.get("message"))
            if isinstance(raw, dict) and raw.get("task_id"): 
                data = LogMessage.trace(task_id=raw.get("task_id"), content=raw.get("content").strip())
        except:
            pass
        self.queue.put(json.dumps(data))
