import time

from rdt import RDTSocket

if __name__ == '__main__':
    server = RDTSocket()
    server.bind(('127.0.0.1', 9999))

    while True:
        conn, client_addr = server.accept()
        start = time.perf_counter()
        while True:
            data = conn.recv(2048)
            if data:
                conn.send(data)
            else:
                break

        conn.close()
        print(f'connection finished in {time.perf_counter() - start}s')
