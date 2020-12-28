import asyncio
import json
import threading
import time

import websockets

# Example `data` format
data = {
    "pkg_count": 1,
    "timeout": 1,
    "flying": 1,
    "congestion": 10,
    "wnd_size": 20,
    "ssthresh": 1
}


async def hello(websocket, path):
    while True:
        await websocket.send(json.dumps(data))
        await asyncio.sleep(3)


def RDTUpdate(key, value):
    data[key] = value


def RDTlog(msg: str, showtime=True, highlight=False):
    instant = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    msg = f"{threading.get_ident()}: {msg}"
    if showtime:
        msg = '[' + instant + ']\t' + msg
    if highlight:
        msg = '\033[93m' + msg + '\033[0m'
    print(msg)


if __name__ == '__main__':
    start_server = websockets.serve(hello, "localhost", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
