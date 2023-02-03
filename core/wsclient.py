import threading
from queue import Queue
# from core.config import cfg
import websocket
from loguru import logger

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
        # logger.info('WebSocket receive message:' + message) # avoid infinite message loop
        pass

    def on_open(self, client):
        logger.success("WebSocket open.")
        # start thread to send logs to websocket
        threading.Thread(target=self.send_loop, daemon=True).start()
        self._reconnect_count = 0

    def on_close(self, client, close_status_code, close_msg):
        if close_status_code or close_msg:
            logger.info("close status code: " + str(close_status_code))
            logger.info("close message: " + str(close_msg))
        logger.info(f"WebSocket closed.{client}")

    def on_ping(self, client, message):
        logger.debug("####### on_ping #######")

    def on_pong(self, client, message):
        logger.debug("####### on_pong #######")

    def on_error(self, client, error):
        logger.error("Websocket connection error!")
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
            logger.error("Unexpected error, close connection!")


if __name__ == '__main__':
    # ws = websocket.WebSocketApp('ws://localhost:8765/', on_message=on_message, on_open=on_open, on_close=on_close)
    # ws.run_forever()
    endpoint = "ws://localhost:8000/api/ws/log/"
    ws = WebSocketClient(server=endpoint, queue=Queue())
    # ws.connect()
    ws.start()
    print('ss')
    logger.debug("closing connection")
    ws.close()
