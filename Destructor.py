import time
from threading import Thread

from utils import RDTlog


class Destructor(Thread):
    def __init__(self, flying, to_send, to_ack, dispatcher, fin_status, timeout):
        super().__init__()
        self.flying = flying
        self.to_send = to_send
        self.to_ack = to_ack
        self.dispatcher = dispatcher
        self.fin_status = fin_status
        self.timeout = timeout
        self.destroyed = False

    def destroy(self):
        self.fin_status[2] = True
        logged = False
        RDTlog("关闭：关闭流程开始", highlight=True)

        # 1. Wait until there is no packet to send
        while self.flying or not self.to_send.empty() or not self.to_ack.empty():
            if not logged:
                logged = True
                RDTlog(f"flying: {self.flying}, to_send length: {self.to_send.qsize()}")
            pass

        RDTlog("关闭：所有队列已清空", highlight=True)

        # 2. Send FIN packet and wait until FIN is acked
        fin_id = self.dispatcher.fill(b'FIN')
        RDTlog("关闭：发送FIN", highlight=True)
        while fin_id in self.flying:
            pass

        logged = False
        while self.flying or not self.to_send.empty() or not self.to_ack.empty():
            if not logged:
                logged = True
                RDTlog(f"> flying: {self.flying}, to_send length: {self.to_send.qsize()}")
            pass

        RDTlog("关闭：所有队列已重新清空", highlight=True)

        RDTlog("关闭：FIN包成功发送并收到回复", highlight=True)

        # 3. Check if FIN is received before, if not, wait.
        while not self.fin_status[1]:
            pass

        RDTlog("关闭：已收到对方的FIN", highlight=True)

        # 4. Stop
        time.sleep(self.timeout[0] * 2)
        self.dispatcher.shutdown()

        self.fin_status[2] = False
        self.fin_status[3] = True
        RDTlog("成功关闭", highlight=True)

    def run(self):
        """
        Run destructor to release all the resource
        """
        if not self.destroyed:
            self.destroyed = True
            self.destroy()
        RDTlog("关闭线程关闭", highlight=True)
