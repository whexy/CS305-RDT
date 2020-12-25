from threading import Thread


class Destructor(Thread):
    def __init__(self, flying, to_send, dispatcher, fin_status):
        super().__init__()
        self.flying = flying
        self.to_send = to_send
        self.dispatcher = dispatcher
        self.fin_status = fin_status
        pass

    def run(self):
        """
        Run destructor to release all the resource
        """

        # 1. Wait until there is no packet to send
        while not self.flying.empty() or not self.to_send.empty():
            pass

        # 2. Send FIN packet and wait until FIN is acked
        self.dispatcher.fill(b'FIN')
        while not self.fin_status[0]:
            pass

        # 3. Check if FIN is received before, if not, wait.
        while not self.fin_status[1]:
            pass

        # 4. Stop
        self.dispatcher.shutdown()
