import subprocess
from loguru import logger
import os


class Console:
    def __init__(self, title=None):
        self.process = None
        self.title = title

    def start(self):
        console_path = r'plugin\console.exe'
        cmd = f"{console_path} {self.title}" if self.title else console_path
        if not os.path.exists(console_path):
            logger.warning(f'{console_path} not exists.')
            return
        self.process = subprocess.Popen(cmd.split(' '), stdin=subprocess.PIPE, universal_newlines=True, bufsize=1,
                                        creationflags=subprocess.CREATE_NEW_CONSOLE, encoding='utf-8')

    def exit(self):
        self.write('console exit\n')

    def write(self, line):
        if not self.process:
            return
        try:
            self.process.stdin.write(line)
            self.process.stdin.flush()
        except Exception as e:
            logger.exception(e)