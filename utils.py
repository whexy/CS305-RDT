import asyncio
import json
import math
import threading
import time
from threading import Thread

import websockets

port = 9988

class RDTUtil(Thread):
    def __init__(self):
        super().__init__()
        self.data = {
            "timeout": 5,
            "flying": 0,
            "wnd_size": 1,
            "ssthresh": 8
        }

        self.startTime = None

        self.is_running = False

    async def hello(self, websocket, path):
        while True:
            if self.is_running:
                self.data["time"] = math.ceil(time.time() - self.startTime)
                await websocket.send(json.dumps(self.data))
            await asyncio.sleep(1)

    def update(self, key, value):
        if self.startTime is None:
            self.startTime = time.time()
        self.is_running = True
        self.data[key] = value

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.hello, "localhost", 8765, loop=loop)
        loop.run_until_complete(start_server)
        loop.run_forever()


def RDTlog(msg: str, showtime=True, highlight=False):
    instant = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    msg = f"{threading.get_ident()}: {msg}"
    if showtime:
        msg = '[' + instant + ']\t' + msg
    if highlight:
        msg = '\033[93m' + msg + '\033[0m'
    print(msg)
