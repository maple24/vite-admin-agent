import os
from queue import Queue

import portalocker
from loguru import logger

from core.wsclient import WebSocketClient
from core.config import cfg
from core.executor import Executor
# from core.consumer import Consumer
# from core.handler import HandlerManager
from core.log import AgentLogger
# from core.task import TaskManager
logger.add(os.path.abspath('log\\agent.log'), rotation="12:00", level='DEBUG')


class Agent:
    def __init__(self):
        self.ws_queue = Queue()
        logger.add(AgentLogger(self.ws_queue).remote_handler, level="INFO") # send log to websocket channel
        self.ws = WebSocketClient(cfg.get_log_ws_url(), self.ws_queue)
        self.executor = Executor()
#         self.topics = [self.executor.host]  # use hostname as the consumer topic
#         self.handler = HandlerManager()
#         self.consumer = Consumer(self.topics, self.handler.dispatch)

    def run(self):
        self.start_wsclient()
#         self.start_consumer()
        self.start_executor()
        self.wait_executor()
#         self.wait_consumer()

#     def start_consumer(self):
#         self.consumer.start()

    def start_wsclient(self):
        self.ws.start()

    def start_executor(self):
        self.executor.start()

#     def wait_consumer(self):
#         self.consumer.join()

    def wait_executor(self):
        self.executor.join()
    
    def close_wsclient(self):
        self.ws.close()

    def _init_log(self):
        # TaskManager.queue = self.ws_queue
        # TaskManager.ws = self.ws
        pass


# allow single process for agent
class Starter:
    def __init__(self):
        self._get_lock()

    def _get_lock(self):
        file_name = os.path.basename(__file__).split('.')[0]
        if os.name == "posix":
            lock_file_name = f"/var/run/{file_name}.pid"
        else:
            lock_file_name = f"{os.path.expanduser('~')}\\{file_name}.pid"
        self.fd = open(lock_file_name, "w")
        try:
            portalocker.lock(self.fd, portalocker.LOCK_EX | portalocker.LOCK_NB)
            self.fd.writelines(str(os.getpid()))
            self.fd.flush()
            logger.info(f"Single instance. lockfile: {lock_file_name}.")
        except:
            logger.error(f"{lock_file_name} have another instance running.")
            exit(1)

    def __del__(self):
        portalocker.unlock(self.fd)



if __name__ == '__main__':
    starter = Starter()  # single process
    agent = Agent()
    agent.run()
