import json
from lib import utils


class AgentLogger:
    def __init__(self, queue):
        self.queue = queue
        self.host = utils.get_host_name()

    def remote_handler(self, message: str):
        data = {
            "purpose": "log",
            "method": "agent_log_message",
            "message": {
                "host": self.host,
                "content": message.strip()
            }
        }
        self.queue.put(json.dumps(data))