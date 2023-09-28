import socket
import sys
import re

class client:

    def __init__(self, server_address, server_port, req_code, msg) -> None:
        
        self.server_address = server_address
        self.server_port = server_port
        self.req_code = req_code
        self.msg = msg
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)

    def connect(self):
        stop = False
        while not stop:
            try:
                self.socket.connect((self.server_address, self.server_port))
                print("Client: Connected to server")
            except socket.timeout:
                pass
            except Exception as e:
                continue
            else:
                stop = True
    
    def send(self):
        try:
            self.socket.sendall(self.req_code.encode())
        except:
            print("Client: Send failed")
            sys.exit()

    def recv(self):
        try:
            data = self.socket.recv(1024)
            return data.decode()
        except:
            print("Client: Receive failed")
            sys.exit()

    def negotiate(self):
        try:
            self.socket.sendall(self.req_code.encode())
            print("Client: Sent code")
            data = self.socket.recv(1024)
            print("Client: Received code", data.decode())
            self.socket.close()
            return data.decode()
        except:
            print("Client: Negotiation failed")
            sys.exit()

    def send_msg(self):
        try:
            self.socket.sendall(self.msg.encode())
        except:
            print("Client: Send failed")
            sys.exit()

clit = client(server_address="127.0.0.1", server_port=50000, req_code="hello", msg=["12414"])
clit.connect()
clit.negotiate()