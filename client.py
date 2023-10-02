import socket
import sys
import re
from typing import Optional
import os
import time
import ipaddress

class tcpclient:

    def __init__(self, server_address, server_port, req_code, msg) -> None:
        
        self.server_address = server_address
        self.server_port = server_port
        self.req_code = req_code
        self.msg = msg
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)

    def connect(self) -> None:
        stop = False
        while not stop:
            try:
                self.socket.connect((self.server_address, self.server_port))
                # print("Client: Connected to server")
            except socket.timeout:
                pass
            except Exception as e:
                continue
            else:
                stop = True

    def negotiate(self) -> Optional[int]:
        try:
            self.socket.send(self.req_code.encode())
            # print("Client: Sent code")
            data = self.socket.recv(1024)
            # print("Client: Received code", data)
            self.socket.close()
            return int(data.decode())
        except Exception as e:
            # print(e)
            # print("Client: Negotiation failed")
            sys.exit()

    def close(self):
        self.socket.close()


class udpclient:

    def __init__(self, server_address, server_port) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.socket.setblocking(False)
        self.server_address = server_address
        self.server_port = server_port

    def send(self, msg: str) -> None:
        self.socket.sendto(msg.encode(), (self.server_address, self.server_port))
        # print("Client: Sent message", msg, (self.server_address, self.server_port))
    
    def recv(self) -> Optional[str]:
        while True:
            try:
                data, _ = self.socket.recvfrom(1024)
                # print("Client: Received message", data.decode())
                return data
            except Exception as e:
                # print(e)
                continue
    
    def bind(self, address, port) -> None:
        self.socket.bind((address, port))
        # print("Client: Bound to address and port")

    def close(self) -> None:
        self.socket.close()
        # print("Client: Closed socket")


def main():

    if len(sys.argv) < 5:
        print("Not enough arguments")
        return 0

    try:
        ipaddress.ip_address(sys.argv[1])
    except Exception as e:
        print("Invalid IP address")
        return 0

    try:
        n_port = int(sys.argv[2])
    except Exception as e:
        print("Invalid port number")
        return 0
    
    # get server_address, n_port, req_code, msgarr
    server_address, n_port, req_code, msgarr = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4:]

    # initiate tcp client
    tcpclit = tcpclient(server_address=server_address, server_port=n_port, req_code=req_code, msg=msgarr)
    
    # connect to server and negotiate
    tcpclit.connect()
    r_port = tcpclit.negotiate()
    tcpclit.close()

    # initiate udp client
    udpclit = udpclient(server_address=server_address, server_port=n_port)
    udpclit.bind("0.0.0.0", r_port)

    res = []
    for msg in msgarr:
        time.sleep(1.5)
        if str(msg) == "EXIT":
            udpclit.send(str(msg))
            udpclit.close()
            break
        udpclit.send(str(msg))
        recv_data = udpclit.recv()

        res.append(str(recv_data.decode())+",")
        if "LIMIT" in recv_data.decode():
            udpclit.close()
            break
    res = " ".join(res)
    print(res[:-1])


if __name__ == "__main__":

    main()


