#!/usr/bin/env python3

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import threading
import argparse
import socket

from packet import Packet
from utils import RepeatTimer

class Sender:
    def __init__(self, ne_host, ne_port, port, timeout, send_file, seqnum_file, ack_file, n_file, send_sock, recv_sock):

        self.ne_host = ne_host
        self.ne_port = ne_port
        self.port = port
        self.timeout = timeout / 1000 # needs to be in seconds

        self.send_file = send_file # file object holding the file to be sent
        self.seqnum_file = seqnum_file # seqnum.log
        self.ack_file = ack_file # ack.log
        self.n_file = n_file # N.log

        self.send_sock = send_sock
        self.recv_sock = recv_sock

        # internal state
        self.lock = threading.RLock() # prevent multiple threads from accessing the data simultaneously
        self.window = [] # To keep track of the packets in the window
        self.window_size = 1 # Current window size 
        self.timer = None # Threading.Timer object that calls the on_timeout function
        self.timer_packet = None # The packet that is currently being timed
        self.current_time = 0 # Current 'timestamp' for logging purposes

    def run(self):
        self.recv_sock.bind(('', self.port))
        self.perform_handshake()
        # write initial N to log
        self.n_file.write('t={} {}\n'.format(self.current_time, self.window_size))
        self.current_time += 1

        recv_ack_thread = threading.Thread(target=sender.recv_ack)
        send_data_thread = threading.Thread(target=sender.send_data)
        recv_ack_thread.start()
        send_data_thread.start()
        
        recv_ack_thread.join()
        send_data_thread.join()
        exit()

    def perform_handshake(self):
        # Send SYN
        packet = Packet(3, 0, 0, "")
        self.send_sock: socket.socket
        timer = RepeatTimer(3, self.send_sock.sendto, [packet.encode(), (self.ne_host, self.ne_port)])
        timer.start()
        # return
        self.transmit_and_log(packet)

        # Wait for SYNACK
        while True:
            recv_packet, addr = self.recv_sock.recvfrom(1024)
            recv_packet = Packet(recv_packet)
            if recv_packet.typ == 3 and recv_packet.seqnum == 0:
                timer.cancel()
                break

        # raise NotImplementedError('perform_handshake not implemented')

        return True

    def transmit_and_log(self, packet: Packet):
        """
        Logs the seqnum and transmits the packet through send_sock.
        """
        # raise NotImplementedError('tramsit_and_log not implemented')

        # Deal with SYN packet
        if packet.typ == 3:
            self.seqnum_file.write("T=-1 SYN\n")
            self.n_file.write("t=0 1\n")

    def recv_ack(self):
        """
        Thread responsible for accepting acknowledgements and EOT sent from the network emulator.
        """
        raise NotImplementedError('recv_ack not implemented')
        return True

    def send_data(self):
        """ 
        Thread responsible for sending data and EOT to the network emulator.
        """
        raise NotImplementedError('send_data not implemented')
        return True

    def on_timeout(self):
        """
        Deals with the timeout condition
        """
        raise NotImplementedError('on_timeout not implemented')
        return True

if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("ne_host", type=str, help="Host address of the network emulator")
    parser.add_argument("ne_port", type=int, help="UDP port number for the network emulator to receive data")
    parser.add_argument("port", type=int, help="UDP port for receiving ACKs from the network emulator")
    parser.add_argument("timeout", type=float, help="Sender timeout in milliseconds")
    parser.add_argument("filename", type=str, help="Name of file to transfer")
    args = parser.parse_args()

    with open(args.filename, 'r') as send_file, open('seqnum.log', 'w') as seqnum_file, \
            open('ack.log', 'w') as ack_file, open('N.log', 'w') as n_file, \
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as send_sock, \
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as recv_sock:
        sender = Sender(args.ne_host, args.ne_port, args.port, args.timeout, 
            send_file, seqnum_file, ack_file, n_file, send_sock, recv_sock)
        sender.run()
