import json
from lib import utils


class LoggerManager:

    def __init__(self, queue):
        self.queue = queue
        self.hostname = utils.get_host_name()

    def remote_logger(self, message: str):
        '''
        send logs to websockets queue
        '''
        data = {
            "purpose": "log",
            "method": "agent_log_message",
            "message": {
                "hostname": self.hostname,
                "content": message.strip()
            }
        }
        self.queue.put(json.dumps(data))