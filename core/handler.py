'''
handler is a class of methods to dispatch message from kafka/websockets
'''
from lib.decorators import Singleton
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from .task import TaskManager


class HandlerManager:
    pool = ThreadPoolExecutor()
    
    def __init__(self) -> None:
        self.handler_map = {
            'task': self.task_handler,
        }
    
    def dispatch(self, key, value):
        if key in self.handler_map:
            handler = self.handler_map[key]
            logger.info(f"Received new task, type: {key}, params: {value}, handler: {handler}")
            try:
                self.pool.submit(handler, value) # if something goes wrong inside the pool, no exception will be raised. so it is hard to debug here!
            except Exception as e:
                logger.exception(e)
        else:
            logger.info(f"{key} not in handler map, discard!")

    @staticmethod
    def task_handler(message):
        try:
            method = message['method']
            args = message['args']
            if hasattr(TaskManager, method):
                logger.debug(f"Task handler get message {method}")
                func = getattr(TaskManager, method)
                func(args)
            else:
                logger.error(f'Method: {method} not exists. Skip!')
        except KeyError:
            logger.exception('Task message format error!')