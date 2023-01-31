import threading
from queue import Queue
# from core.config import cfg
import websocket
from loguru import logger

websocket.enableTrace(False)


class WebSocketClient(threading.Thread):
    def __init__(self, queue: Queue, server):
        super().__init__(target=self.connect)
        self.ws = None
        self.server = server
        self.queue = queue
        self._reconnect_count = 0
        self._MAX_RECONNECT_LIMIT = 100
        self._forever = True
        self.send_thread = threading.Thread(target=self.send_loop, daemon=True)
        self.send_thread.start()

    def connect(self):
        self.ws = websocket.WebSocketApp(self.server, on_message=self.on_message, on_open=self.on_open,
                                         on_close=self.on_close, on_error=self.on_error, on_ping=self.on_ping,
                                         on_pong=self.on_pong)
        try:
            self.ws.run_forever()
        except AttributeError:
            pass
        except Exception as e:
            logger.error(e)

    def send(self, message):
        try:
            self.ws.send(message)
        except Exception as e:
            # logger.error(e)
            pass

    def send_loop(self):
        while True:
            message = self.queue.get()
            self.send(message)

    def close(self):
        self.ws.close()

    def on_message(self, client, message):
        # logger.info('WebSocket receive message:' + message)
        pass

    def on_open(self, client):
        logger.info("WebSocket open.")
        self._reconnect_count = 0

    def on_close(self, client, code, message):
        logger.info(f"WebSocket closed.{client}, {code}, {message}")

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
            logger.error(type(error), error)


if __name__ == '__main__':
    # ws = websocket.WebSocketApp('ws://localhost:8765/', on_message=on_message, on_open=on_open, on_close=on_close)
    # ws.run_forever()
    ws = WebSocketClient(Queue())
    # ws.connect()
    ws.start()
    print('ss')
    ws.close()
    pass
