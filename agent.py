import os
from queue import Queue

import portalocker
from loguru import logger

from core.wsclient import WebSocketClient
from core.config import cfg
from core.executor import Executor
from core.consumer import MessageConsumer
from core.handler import HandlerManager
from core.log import LoggerManager
logger.add(os.path.abspath('log\\agent.log'), rotation="12:00", level='DEBUG')


class Agent:
    def __init__(self):
        self.ws_queue = Queue() # log queue
        self.ws = WebSocketClient(cfg.get_log_ws_url(), self.ws_queue) # websockets
        self.executor = Executor() # agent executor
        self.hostname = self.executor.hostname
        self.handler = HandlerManager() # handler to dispatch tasks
        self.consumer = MessageConsumer(
            topic=[self.hostname], 
            group_id=self.hostname, 
            callback=self.handler.dispatch) # consume kafka messages
        logger.add(LoggerManager(self.ws_queue).remote_logger, level="INFO") # add logger to log queue

    def run(self):
        self.start_wsclient()
        self.start_consumer()
        self.start_executor()
        self.wait_consumer()
        self.wait_executor()

    def start_consumer(self):
        self.consumer.setDaemon(True)
        self.consumer.start()

    def start_wsclient(self):
        self.ws.start()

    def start_executor(self):
        self.executor.start()

    def wait_consumer(self):
        self.consumer.join()

    def wait_executor(self):
        self.executor.join()
    
    def close_wsclient(self):
        self.ws.close()


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
