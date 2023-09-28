import socket
import sys
import re
import random

class tcpserver:

    def __init__(self, req_code, limit) -> None:

        self.req_code = req_code
        self.limit = limit
        self.client_addr = None
        self.client_port = None
        self.r_port = random.randint(1024, 65535)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.settimeout(10)

    def bind(self, address, port):
        try:
            self.socket.bind((address, port))
            print("Bind successful")
        except Exception as e:
            print(e)
            sys.exit()

    def negotiate(self):
        stopped = False
        self.socket.listen(1)
        while not stopped:
            try: 
                (conn, (ip, port)) = self.socket.accept()
                print("server connected to client")
            except socket.timeout:
                pass
            else:
                stopped = True
                conn.sendall(self.req_code.encode())
                print("server sent code")
                self.socket.close()
                return ip, port



servr = tcpserver(req_code="hello", limit=5)
servr.bind("127.0.0.1", 50000)
ip, port = servr.negotiate()
    

