import socket
import sys
import re
import random
import time
import string
from multiprocessing import Process
from typing import Optional

class tcpserver:

    def __init__(self, req_code) -> None:

        self.req_code = req_code
        self.client_addr = None
        self.client_port = None
        self.r_port = -1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.count = 0

        self.socket.settimeout(10)

    def bind(self, address, port):
        try:
            self.socket.bind((address, port))
            # print("Bind successful")
        except Exception as e:
            # print(e)
            sys.exit()

    def negotiate(self):
        stopped = False
        self.socket.listen(1)
        while not stopped:
            try: 
                (conn, (ip, port)) = self.socket.accept()
                client_req_code = conn.recv(1024)
                # print("server connected to client")
            except socket.timeout:
                pass
            else:
                if client_req_code.decode() != self.req_code:   
                    print("server received wrong code")
                    self.socket.close()
                    return None, None
                stopped = True
                self.r_port = random.randint(1024, 65535)
                while self.socket.connect_ex((ip, self.r_port)) == 0:
                    self.r_port = random.randint(1024, 65535)
                conn.sendall(str(self.r_port).encode())
                # print("server sent code", self.r_port)
                return ip, port
            
    def palindrome(self, msg):
        msg = msg.lower()
        msg = re.sub(r"[^a-z]", "", msg)
        return msg == msg[::-1]
    
    def close(self):
        self.socket.close()

class udpserver:

    def __init__(self, limit) -> None:
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.socket.setblocking(False)
        self.limit = limit
        self.count = 0

    def bind(self, address, port) -> None:
        self.socket.bind((address, port))
        # print("server bound to address and port")

    def send(self, msg, addr) -> None:
        self.socket.sendto(str(msg).encode(), addr)
        # print("server sent message", bytes(msg))

    def recv(self):
        # while True:
        #     try:
        while True:
            try:
                data, address = self.socket.recvfrom(1024)
                # print("server received message", data)
                return data.decode(), address
            except Exception as e:
                continue
            # except socket.timeout:
            #     pass
            # except Exception as e:
            #     # print(e)
            #     continue
    
    def palindrome(self, msg): # TODO
        msg = msg.lower()
        translator = str.maketrans("", "", string.punctuation)
        msg = msg.translate(translator)
        return msg == msg[::-1]
    
    def run(self):

        while True:
            data, addr = self.recv()
            # print("server connected to client")
            self.count += 1
            if data == "EXIT":
                # print("server received EXIT")
                self.socket.close()
                break

            # print("address: ", addr)

            # print(type(self.count), type(self.limit))
            if self.count == self.limit:
                self.send("{0}, LIMIT".format(self.palindrome(data)), addr)
                self.count = 0
                self.socket.close()
                break
            else:
                self.send(self.palindrome(data), addr)
            # self.send(self.palindrome(data), addr)
            # print("server sent data", self.palindrome(data))

            # if self.count == self.limit:
            #     self.send("EXIT", addr)
            #     self.count = 0


def main():

    # print(sys.argv)
    if len(sys.argv) != 3:
        print("Invalid number of arguments")
        return 0
    if not sys.argv[2].isdigit():
        print("Invalid limit")
        return 0
    if int(sys.argv[2]) < 0:
        print("Invalid limit")
        return 0


    # get req_code and req_lim from command line
    req_code, req_lim = sys.argv[1], int(sys.argv[2])

    # create tcpserver object
    servr = tcpserver(req_code=req_code)

    # bind to address and port
    servr.bind("0.0.0.0", 0)

    server_port = servr.socket.getsockname()[1]
    print("SERVER_PORT=" + str(server_port))

    # negotiate with client
    client_ip, client_port = servr.negotiate()

    if client_ip == None or client_port == None:
        sys.exit()
    
    # close tcpserver
    servr.close()
    # print("Stage 1 complete")

    # create udpserver object
    servr = udpserver(limit=req_lim)
    
    # bind to address and port
    servr.bind("0.0.0.0", server_port)
    
    # run udpserver to handle client requests
    servr.run()


        
if __name__ == "__main__":

    main()