'''
an agent executor is to create and  maintain connection with backend server
'''
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time
from lib import utils
from core.config import cfg
from core.task import TaskManager
from loguru import logger
from api.api import http_api
from lib.decorators import Singleton


@Singleton
class Executor:

    def __init__(self):
        self.root = cfg.get('local').get('root')  # data root of rf
        self.ip = utils.get_ip()  # ip of executor
        self.hostname = utils.get_host_name()
        self.scripts = []  # available scripts
        self._register()
        self.heartbeat_thread = threading.Thread(target=self.heartbeat)
        self.scan_scripts_thread = threading.Thread(target=self.scan_scripts)

    def start(self):
        self.scan_scripts_thread.start()
        self.heartbeat_thread.start()

    def join(self):
        self.scan_scripts_thread.join()
        self.heartbeat_thread.join()

    def scan_scripts(self):
        while True:
            scripts = utils.list_files(self.root, '.bat')
            if self.scripts != scripts:
                logger.info("Scripts update!")
                self.scripts = scripts
                self._register()
            time.sleep(5)

    def heartbeat(self):
        while True:
            http_api.heartbeat(
                ip=self.ip,
                hostname=self.hostname,
                task_list=TaskManager.all(),
                is_active=utils.is_active()
            )
            time.sleep(3)

    def _register(self):
        while True:
            if http_api.register(
                ip=self.ip,
                hostname=self.hostname,
                scripts=self.scripts
            ): break
            time.sleep(3) # reconnect every 3s


if __name__ == '__main__':
    executor = Executor()
    executor.start()
