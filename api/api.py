import os
import sys
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from requests.exceptions import ConnectionError
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
            'register': '/api/v1/agent/executor/register/',
            'getTask': '/api/v1/agent/task/{0}',
            'updateTask': '/api/v1/agent/task/{0}/',
            'login': '/api/v1/auth/login/'
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
        logger.debug(f"Response get {url} return with code: {res.status_code}")
        if res.status_code == 200:
            return res.text
        else:
            return

    @staticmethod
    def post(url, data=None):
        logger.debug(f"Request post {url}. data: {data}")
        res = requests.post(url, json=data, headers={"Content-Type": 'application/json'})
        logger.debug(f"Response post {url} return with code: {res.status_code}")
        if res.status_code == 201:
            return ResponseMessage(json.loads(res.text))
        else:
            return ResponseMessage()

    @staticmethod
    def put(url, data=None):
        logger.debug(f"Request post {url}. data: {data}")
        res = requests.put(url, json=data, headers={"Content-Type": 'application/json'})
        logger.debug(f"Response post {url} return with code: {res.status_code}")
        if res.status_code == 201:
            return ResponseMessage(json.loads(res.text))
        else:
            return ResponseMessage()

    @staticmethod
    def patch(url, data=None):
        '''
        json.dumps is used along with application.json
        django drf default method is used data instead of json
        set default to str to convert everything it doesn't know to strings like data aren't serializable
        '''
        logger.debug(f"Request post {url}. data: {data}")
        res = requests.patch(url, data=json.dumps(data, default=str), headers={"Content-Type": 'application/json'})
        logger.debug(f"Response post {url} return with code: {res.status_code}")
        if res.status_code == 200:
            return True
        else:
            return False

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

    def update_task(self, **kwargs):
        '''
        update_task(task_id=1, status='Completed')
        '''
        task_id = kwargs.get('task_id')
        url = self._get_url('updateTask').format(task_id)
        try:
            res = self.patch(url, data=kwargs)
            if res:
                logger.debug(f"Update task `{task_id}` with args `{kwargs}` success. {str(res)}")
                return True
            else:
                logger.error(f"Update task `{task_id}` with args `{kwargs}` fail. {str(res)}")
        except Exception as e:
            logger.exception(e)

    def login(self, **kwargs):
        url = self._get_url('login')
        try:
            res = requests.post(url, data=json.dumps(kwargs), headers={"Content-Type": 'application/json'})
            if res.status_code == 200:
                return True
        except Exception as e:
            logger.exception(e)

http_api = HttpRequest()

if __name__ == '__main__':
    r = HttpRequest()
    # data = {"ip": "172.21.160.1", "hostname": "SZH-C-0075C"}
    # res = http_api.register(ip=data.get("ip"), hostname=data.get("hostname"))
    # print(res)
    # pass
    # print(r.patch(url=r._get_url('updateTask').format(1), data={'status': 'Completed'}))
    print(r.login(username="ziu7wx", password="zj#7829369041"))