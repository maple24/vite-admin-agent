'''
Task: task object
TaskManager: control task flow and report status to backend
'''
import subprocess
from api.api import http_api
from loguru import logger
import psutil
import os
from .config import cfg
from .console import Console
import datetime


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
    def __init__(self, task_id, script=None, params=None):
        self.task_id = task_id
        self._status = TaskStatus.IDLING
        self.process = None
        self.params = params
        self.script = script
        self.console = None
        self.reason = None
        
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
        cmd = self.script + ' ' + self.params if self.params else self.script
        logger.info(f'start cmd: {cmd}')
        # error also displays in outpipe
        self.process = subprocess.Popen(cmd.split(' '), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        out = self.process.stdout
        if console: # output to console line by line
            self.init_console(title=f"TASK:{self.task_id}")
            while True:
                if self.process.poll() is not None: break
                line = out.readline().decode('utf-8')
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
        parent = psutil.Process(self.process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
        logger.debug(f'Terminate task: {self.task_id} finished.')        

    def init_console(self, title=None):
        self.console = Console(title)
        self.console.start()
    
    @staticmethod
    def report_status(task_id, status):
        http_api.update_task(task_id=task_id, status=status)
    
    @staticmethod
    def report_end_time(task_id, reason):
        if reason:
            http_api.update_task(task_id=task_id, end_time=datetime.datetime.now().replace(microsecond=0), schedule_id=None, reason=reason)
        else:
            http_api.update_task(task_id=task_id, end_time=datetime.datetime.now().replace(microsecond=0), schedule_id=None)

    @staticmethod
    def report_start_time(task_id):
        http_api.update_task(task_id=task_id, start_time=datetime.datetime.now().replace(microsecond=0))
    


class TaskManager:
    
    container = {}
    ROOT = cfg.get('local').get('root')
    
    @classmethod
    def _init_task(cls, args: dict) -> Task:
        task_id=args.get("task_id")
        if task_id in cls.container:
            logger.warning(f"Task {task_id} already in processing. Skip!")
            return
        script = os.path.join(cls.ROOT, args.get("script"))
        params = args.get("params")
        task = Task(task_id, script, params)
        logger.success("Task initiated!")
        if not os.path.exists(script):
            logger.warning(f"{script} not exist.")
            task.status = TaskStatus.ERROR
            Task.report_end_time(task.task_id, f"{script} not exist!")
            return
        cls._add_task(task_id, task)
        task.status = TaskStatus.STARTING
        return task
    
    @classmethod
    def _add_task(cls, task_id, task):
        cls.container.setdefault(task_id, task)
    
    @classmethod
    def _remove_task(cls, task_id):
        if task_id in cls.container: cls.container.pop(task_id)
    
    @classmethod
    def _fetch_task(cls, task_id) -> Task:
        '''
        specify type of output, vscode can auto-complete method of the instance
        '''
        return cls.container.get(task_id)

    @classmethod
    def all(cls):
        return list(cls.container.keys())
    
    @classmethod
    def start_task(cls, args: dict, console=True):
        logger.success(f"Start task: {args}")
        task = cls._init_task(args)
        Task.report_start_time(task.task_id)
        task.status = TaskStatus.RUNNING
        logger.debug("Start running task!")
        try:
            task.run(console)
            if task.process.poll() == 0:
                # 0 == normal exit; 15 == kill; None == child process is still running;
                task.status = TaskStatus.COMPLETED
                logger.debug("Task completed!")
        except Exception as e:
            logger.debug("Error occured when running task!")
            task.reason = "Error occured when running task!"
            task.status = TaskStatus.ERROR
            logger.exception(e)
        finally:
            cls._remove_task(task.task_id)
            Task.report_end_time(task.task_id, task.reason)
    
    @classmethod
    def stop_task(cls, args: dict):
        logger.warning(f'Stop task: {args}')
        task_id = args.get('task_id')
        if task_id not in cls.container:
            logger.warning(f"Task {task_id} not in processing. Skip!")
            Task.report_status(task_id, TaskStatus.TERMINATED)
            Task.report_end_time(task_id, "Task not exist in container!")
            return
        task = cls._fetch_task(task_id)
        try:
            task.terminate()
            logger.debug("Task terminated!")
            task.status = TaskStatus.TERMINATED
            task.reason = "Force terminated by user."
        except Exception as e:
            task.status = TaskStatus.ERROR
            task.reason = "Terminate task error!"
            logger.exception(e)
        finally:
            cls._remove_task(task_id)
            Task.report_end_time(task_id, task.reason)
        

if __name__ == '__main__':
    task1 = {
        'task_id': 1,
        'script': 'run.bat',
        'params': ''
    }
    TaskManager.start_task(task1)
    