'''
create websockets client
'''
import threading
from queue import Queue
import websocket
from loguru import logger
import json
from lib.utils import run_command, get_host_name
from lib.message import LogMessage


websocket.enableTrace(False)


class WebSocketClient(threading.Thread):
    def __init__(self, server, queue: Queue):
        super().__init__(target=self.connect)
        self.server = server
        self.queue = queue
        self._reconnect_count = 0
        self._MAX_RECONNECT_LIMIT = 100
        self._forever = True

    def connect(self):
        self.ws = websocket.WebSocketApp(self.server, on_message=self.on_message, on_open=self.on_open,
                                         on_close=self.on_close, on_error=self.on_error, on_ping=self.on_ping,
                                         on_pong=self.on_pong)
        self.ws.run_forever()

    def send(self, message):
        self.ws.send(message)

    def send_loop(self):
        while True:
            message = self.queue.get()
            self.send(message)

    def close(self):
        self.ws.close()

    def on_message(self, client, message):
        # to avoid infinite message loop, do not use logger
        args = json.loads(message).get("args")
        if isinstance(args, dict):
            if args.get("command") and args.get("hostname") == get_host_name():
                try:
                    result = run_command(cmd=args.get("command"), input=args.get("input"))
                except Exception as e:
                    logger.debug(e)
                data = LogMessage.output(hostname=args.get("hostname"), output=result)
                self.send(json.dumps(data)) # also can use logger here, depends on whether you want it to show in the local terminal

    def on_open(self, client):
        logger.success("WebSocket open.")
        # start thread to send logs to websocket
        threading.Thread(target=self.send_loop, daemon=True).start()
        self._reconnect_count = 0

    def on_close(self, client, close_status_code, close_msg):
        # reconnect
        if close_status_code or close_msg:
            logger.info("close status code: " + str(close_status_code))
            logger.info("close message: " + str(close_msg))
        logger.info(f"WebSocket closed.{client}")
        if self._forever:
            logger.info("WebSocket closed. Try reconnecting...")
            self.connect()

    def on_ping(self, client, message):
        logger.debug("####### on_ping #######")

    def on_pong(self, client, message):
        logger.debug("####### on_pong #######")

    def on_error(self, client, error):
        error_list = [ConnectionResetError, ConnectionRefusedError, websocket._exceptions.WebSocketConnectionClosedException]
        if type(error) in error_list:
            if self._forever:
                logger.info(f"WebSocket connect error, try to reconnect.")
                self.close()
                self.connect()
            elif self._reconnect_count < self._MAX_RECONNECT_LIMIT:
                logger.info(
                    f"WebSocket connect error, try to reconnect. {self._reconnect_count}/{self._MAX_RECONNECT_LIMIT}")
                self._reconnect_count += 1
                self.close()
                self.connect()
        else:
            logger.error("Unexpected error >>" + error)


if __name__ == '__main__':
    endpoint = "ws://localhost:8000/api/ws/log/"
    ws = WebSocketClient(server=endpoint, queue=Queue())
    ws.start()
    print('ss')
    logger.debug("closing connection")
    ws.close()
