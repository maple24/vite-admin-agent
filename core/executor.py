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
# from core.task import TaskManager
from loguru import logger
from api.api import http_api
from lib.decorators import Singleton


@Singleton
class Executor:

    def __init__(self):
        self.ip = utils.get_ip()  # ip of executor
        self.hostname = utils.get_host_name()
        self._register()
        self.heartbeat_thread = threading.Thread(target=self.heartbeat)
        self.root = cfg.get('local').get('root')  # data root of rf
        self.bats = []  # bats of rf
        # self.scan_scripts_thread = threading.Thread(target=self.scan_scripts)

    def start(self):
        # self.scan_scripts_thread.start()
        self.heartbeat_thread.start()

    def join(self):
        # self.scan_scripts_thread.join()
        self.heartbeat_thread.join()

    def scan_scripts(self):
        while True:
            bats = utils.list_files(self.root, '.bat')
            if self._check_updated(bats):
                logger.info("Scripts update! Trigger register method to report to platform.")
                self.bats = bats
                self._register()
            time.sleep(5)

    def heartbeat(self):
        while True:
            http_api.heartbeat(
                ip=self.ip,
                hostname=self.hostname,
                # task_list=TaskManager.all()
            )
            time.sleep(5)

    def _check_updated(self, bats):
        flag = False
        old = self.bats
        new = bats
        for bat in new:
            if bat not in old:
                logger.info(f"Script found: {bat['name']}")
                flag = True
        for bat in old:
            if bat not in new:
                logger.info(f"Script deleted: {bat['name']}")
                flag = True
        return flag

    def _register(self):
        _is_registered = False
        while not _is_registered:
            _is_registered = http_api.register(
                ip=self.ip,
                hostname=self.hostname,
                # script=self.bats
            )
            time.sleep(3) # reconnect every 3s


if __name__ == '__main__':
    executor = Executor()
    executor.start()
