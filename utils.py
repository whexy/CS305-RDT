import asyncio
import json
import math
import threading
import time
from threading import Thread

import websockets


class RDTUtil(Thread):
    def __init__(self):
        super().__init__()
        self.data = {
            "pkg_count": 1,
            "timeout": 1,
            "flying": 1,
            "congestion": 10,
            "wnd_size": 20,
            "ssthresh": 1
        }

        self.startTime = time.time()

        self.is_running = False

    async def hello(self, websocket, path):
        while True:
            if self.is_running:
                self.data["time"] = math.ceil(time.time() - self.startTime)
                await websocket.send(json.dumps(self.data))
            await asyncio.sleep(1)

    def RDTUpdate(self, key, value):
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
