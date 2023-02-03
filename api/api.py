import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
from requests.exceptions import ConnectionError
import requests
from loguru import logger
from core.config import cfg


class ResponseMessage:
    def __init__(self, response=None):
        self.response = response
        if response:
            self.code = response['code']
            self.reason = response['reason']
            self.objects = response['objects']
        else:
            self.code = None
            self.reason = None
            self.objects = None

    def is_positive(self):
        return True if self.code == 'ok' else False

    def __str__(self):
        return str(self.response)


class HttpRequest:
    def __init__(self):
        self.base_url = self._get_base()
        self.route = {
            'heartbeat': '/api/v1/agent/executor/heartbeat/',
            'updateStatus': '/api/v1/web/updateStatus/',
            'getTask': '/api/v1/web/task/{0}/check_task_status/',
            'updateTask': '/api/v1/web/task/{0}/update_task_status/',
            'register': '/api/v1/agent/executor/register/',
            'register1': '/api/v1/agent/executor/'
        }

    @staticmethod
    def _get_base():
        platform = cfg.get('platform')
        return f"http://{platform.get('ip')}:{platform.get('port')}"

    def _get_url(self, key):
        base = self.base_url[:-1] if self.base_url.endswith('/') else self.base_url
        return base + self.route[key]

    @staticmethod
    def get(url, params=None):
        logger.debug(f"Request get {url}. params: {params}")
        res = requests.get(url, params)
        logger.debug(f"Response get {url} return with code: {res.status_code}, {res.text}")
        if res.status_code == 200:
            return res.text
        else:
            return

    @staticmethod
    def post(url, data=None):
        logger.debug(f"Request post {url}. data: {data}")
        res = requests.post(url, json=data, headers={"Content-Type": 'application/json'})
        logger.debug(f"Response post {url} return with code: {res.status_code}, {res.text}")
        if res.status_code == 200:
            return ResponseMessage(json.loads(res.text))
        else:
            return ResponseMessage()

    def heartbeat(self, **kwargs):
        url = self._get_url('heartbeat')
        try:
            res = self.post(url, data=json.dumps(kwargs))
            # res = self.post(url, data=kwargs)
            if res.is_positive():
                logger.success("heartbeat success.")
            else:
                logger.warning(f"heartbeat fail. {str(res)}")
        except ConnectionError:
            logger.error("Proxy Error")
        except Exception as e:
            logger.exception(e)

    def register(self, **kwargs):
        url = self._get_url('register')
        try:
            # res = self.post(url, data=json.dumps(kwargs))
            res = self.post(url, data=json.dumps(kwargs))
            if res.is_positive():
                logger.success("Register success.")
                return True
            else:
                logger.error(f"Register fail. {str(res)}")
        except ConnectionError:
            logger.error("Proxy Error")
        except Exception as e:
            logger.exception(e)

    def get_task(self, task_id):
        url = self._get_url('getTask').format(task_id)
        task = None
        try:
            res = self.post(url)
            if res.is_positive():
                task = res.objects
            else:
                logger.warning(f"Get task: {task_id} fail. {str(res)}")
        except ConnectionError:
            logger.error("Proxy Error")
        except Exception as e:
            logger.exception(e)
        return task

    def update_task(self, task_id, status):
        url = self._get_url('updateTask').format(task_id)
        try:
            res = self.post(url, data=json.dumps({'status': status}))
            if res.is_positive():
                return True
            else:
                logger.warning(f"Update task: {task_id} fail. {str(res)}")
                return False
        except Exception as e:
            logger.exception(e)
            return False


http_api = HttpRequest()

if __name__ == '__main__':
    # r = HttpRequest()
    # http_api.heartbeat()
    pass
