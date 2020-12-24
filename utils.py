import threading
import time


def RDTlog(msg: str, showtime=True, highlight=False):
    instant = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    msg = f"{threading.get_ident()}: {msg}"
    if showtime:
        msg = '[' + instant + ']\t' + msg
    if highlight:
        msg = '\033[93m' + msg + '\033[0m'
    print(msg)


if __name__ == '__main__':
    # A single example program to show how to use these utils
    RDTlog("Hello World!")
    RDTlog("Hello World!", highlight=True)