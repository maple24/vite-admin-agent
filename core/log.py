import json
from lib import utils


class AgentLogger:
    def __init__(self, queue):
        self.queue = queue
        self.hostname = utils.get_host_name()

    def remote_handler(self, message: str):
        data = {
            "purpose": "log",
            "method": "agent_log_message",
            "message": {
                "hostname": self.hostname,
                "content": message.strip()
            }
        }
        self.queue.put(json.dumps(data))