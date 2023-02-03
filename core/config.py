import os.path

import yaml
from loguru import logger
from lib.decorators import Singleton

@Singleton
class Config:
    def __init__(self, file='conf\\config.yml'):
        self._conf = {}
        self._file = file
        self.load()

    def load(self):
        try:
            with open(self._file, encoding='utf-8') as f:
                self._conf = yaml.load(f, Loader=yaml.SafeLoader)
                logger.success(f"Load config file success:{self._conf}")
        except FileNotFoundError:
            logger.exception(f"File not found: {self._file}")
            exit()
        except Exception as e:
            logger.exception(e)
            exit()

    def get(self, key):
        return self._conf.get(key)

    def get_all(self):
        return self._conf

    def get_log_ws_url(self):
        return f'ws://{self.get("platform").get("ip")}:{self.get("platform").get("port")}/api/ws/log/'


cfg = Config()


if __name__ == '__main__':
    file = '..\conf\config2.yml'
    cfg = Config(file)
    logger.info(cfg.get_all())
    logger.info(cfg.get('kafka').get('topic'))
