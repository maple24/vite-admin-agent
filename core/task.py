'''
Task: task object
TaskManager: control task flow and report status to backend
'''
import subprocess
import threading
from api.api import http_api
from loguru import logger
import psutil
import os
from lib.decorators import Singleton
from .config import cfg
from .console import Console
import datetime
from lib.message import LogMessage


class TaskStatus:
    IDLING = 'Idling'
    STARTING = 'Starting'
    RUNNING = 'Running'
    COMPLETED = 'Completed'
    ERROR = 'Error'
    TERMINATED = 'Terminated'
    QUEUING = 'Queuing'
    PUBLISHED = 'Published'
    CANCELED = 'Canceled'
    SCHEDULED = 'Scheduled'
    
    
class Task:
    def __init__(self, task_id, target=None, script=None, params=None):
        self.task_id = task_id
        self._status = TaskStatus.IDLING
        self.process = None
        self.params = params
        self.script = script
        # TODO: target is not necessary
        self.target = target
        self.console = None
        
    @property
    def title(self):
        return f'{self.task_id}_{self.script}'
        
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        self.report_status(task_id=self.task_id, status=self.status)

    def run(self, console: bool=False):
        '''
        run task and wait it done
        '''
        cmd = self.script + ' ' + self.params
        logger.info(f'start cmd: {cmd}')
        # error also displays in outpipe
        self.process = subprocess.Popen(cmd.split(' '), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        out = self.process.stdout
        if console: # output to console line by line
            self.init_console(title=f"TASK:{self.task_id}")
            while True:
                line = out.readline().decode('utf-8')
                if not line: break
                self.console.write(line)
                logger.trace({
                    "task_id": self.task_id,
                    "content": line 
                })
            # self.console.exit()
        else:
            for o in out.readlines():
                logger.info(o.decode())

    def terminate(self):
        '''
        terminate process and its child process
        '''
        try:
            children = psutil.Process(self.process.pid).children()
        except psutil.NoSuchProcess:
            logger.debug(f"PID {self.process.pid} not exist.")
            return
        for child in children:
            logger.debug(f"Terminate task: {self.task_id} pid: {child.pid}")
            os.popen('taskkill.exe /f /pid:' + str(child.pid))
        logger.debug(f'Terminate task: {self.task_id} finished.')        

    def init_console(self, title=None):
        self.console = Console(title)
        self.console.start()
    
    @staticmethod
    def report_status(task_id, status):
        http_api.update_task(task_id=task_id, status=status)
    
    @staticmethod
    def report_end_time(task_id):
        http_api.update_task(task_id=task_id, end_time=datetime.datetime.now())

    @staticmethod
    def report_start_time(task_id):
        http_api.update_task(task_id=task_id, start_time=datetime.datetime.now())
    

@Singleton
class TaskManager:
    
    def __init__(self) -> None:
        self.container = {}
        self.ROOT = cfg.get('local').get('root')
    
    def _init_task(self, args: dict) -> Task:
        task_id=args.get("task_id")
        if task_id in self.container:
            logger.warning(f"Task {task_id} already in processing. Skip!")
            return
        script = os.path.join(self.ROOT, args.get("script"))
        target = args.get("target")
        params = args.get("params")
        task = Task(task_id, target, script, params)
        logger.debug("Task initiated!")
        if not os.path.exists(script):
            logger.warning(f"{script} not exist.")
            task.status = TaskStatus.ERROR
            return
        self._add_task(task_id, task)
        task.status = TaskStatus.STARTING
        return task
    
    def _add_task(self, task_id, task):
        self.container.setdefault(task_id, task)
    
    def _remove_task(self, task_id):
        if task_id in self.container: self.container.pop(task_id)
    
    def _fetch_task(self, task_id) -> Task:
        '''
        specify type of output, vscode can auto-complete method of the instance
        '''
        return self.container.get(task_id)
    
    def start_task(self, args: dict, console=True):
        logger.success(f"Start task: {args}")
        task = self._init_task(args)
        Task.report_start_time(task.task_id)
        task.status = TaskStatus.RUNNING
        logger.debug("Start running task!")
        try:
            task.run(console)
            task.status = TaskStatus.COMPLETED
            logger.debug("Task completed!")
        except Exception as e:
            logger.debug("Error occured when running task!")
            task.status = TaskStatus.ERROR
            logger.exception(e)
        finally:
            self._remove_task(task.task_id)
            Task.report_end_time(task.task_id)
            logger.success(f"Task {task.task_id} completed!")
    
    def stop_task(self, args: dict):
        logger.warning(f'Stop task: {args}')
        task_id = args.get('task_id')
        if task_id not in self.container:
            logger.warning(f"Task {task_id} not in processing. Skip!")
            Task.report_status(task_id, TaskStatus.TERMINATED)
            Task.report_end_time(task_id)
            return
        task = self._fetch_task(task_id)
        try:
            task.terminate()
            logger.debug("Task terminated!")
            task.status = TaskStatus.TERMINATED
            Task.report_end_time(task_id)
        except Exception as e:
            logger.exception(e)
        finally:
            self._remove_task(task_id)
        

if __name__ == '__main__':
    task1 = {
        'task_id': 1,
        'script': 'run.bat',
        'target': '',
        'params': ''
    }
    taskManager = TaskManager()
    taskManager.start_task(task1)
    