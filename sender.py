#!/usr/bin/env python3

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import threading
import argparse
import socket
import queue

from packet import Packet
from utils import RepeatTimer, Watcher, log_file

EOT = False

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
        self.window = [] # To keep track of the packets in the window, format: [packet_1, packet_2, ...]
        self.window_size = 1 # Current window size 
        self.timer = None # Threading.Timer object that calls the on_timeout function
        self.timer_packet = None # The packet that is currently being timed
        self.current_time = 0 # Current 'timestamp' for logging purposes
        self.data_size = 500 # Maximum size of data in a packet

        self.fifo = queue.Queue() # FIFO queue to hold all the data packets
        self.eot_timer = RepeatTimer(3, self.send_eot)

    def run(self):
        self.init_fifo()
        self.recv_sock.bind(('', self.port))
        self.perform_handshake()
        # write initial N to log
        self.n_file.write('t={} {}\n'.format(self.current_time, self.window_size))
        self.current_time += 1

        self.timer = Watcher()
        self.timer.start()
        recv_ack_thread = threading.Thread(target=self.recv_ack)
        send_data_thread = threading.Thread(target=self.send_data)
        recv_ack_thread.start()
        send_data_thread.start()
        
        recv_ack_thread.join()
        send_data_thread.join()
        exit()

    def perform_handshake(self):
        # Send SYN

        timer = RepeatTimer(3, self.send_syn)
        timer.start()

        # Wait for SYNACK
        while True:
            recv_packet, _ = self.recv_sock.recvfrom(1024)
            recv_packet = Packet(recv_packet)
            if recv_packet.typ == 3 and recv_packet.seqnum == 0:
                timer.cancel()
                break
        # raise NotImplementedError('perform_handshake not implemented')


    def transmit_and_log(self, packet: Packet):
        """
        Logs the seqnum and transmits the packet through send_sock.
        """

        self.send_sock.sendto(packet.encode(), (self.ne_host, self.ne_port))
        log_file(self.current_time, packet.seqnum, self.seqnum_file, 'seqnum')
        self.current_time += 1



    def recv_ack(self):
        """
        Thread responsible for accepting acknowledgements and EOT sent from the network emulator.
        """

        while True:
            recv_pkt = self.recv_sock.recvfrom(1024)
            recv_pkt = Packet(recv_pkt)

            if recv_pkt.typ == 0:
                # Deal with ACK packet
                self.window_size = min(10, self.window_size+1)
                self.n_file.write('t={} {}\n'.format(self.current_time, self.window_size))
                self.lock.acquire()
                self.update_window(recv_pkt.seqnum)
                self.lock.release()
                log_file(self.current_time, recv_pkt.seqnum, self.ack_file, 'ack')
                self.current_time += 1

            if recv_pkt.typ == 2:
                EOT = True
                self.eot_timer.cancel()

            if EOT == True and len(self.window) == 0:
                self.send_sock.close()
                self.recv_sock.close()
                break
            



    def send_data(self):
        """ 
        Thread responsible for sending data and EOT to the network emulator.
        """

        while True:

            if self.on_timeout():
                self.window_size = 1
                self.n_file.write('t={} {}\n'.format(self.current_time, self.window_size))
                if len(self.window) == 0:
                    continue
                self.transmit_and_log(self.window[0])

            if len(self.window) == 0 and self.fifo.empty() and self.eot_timer.run_started == False:
                self.eot_timer.start()

            if self.eot_timer.run_finished == True:
                break

            if len(self.window) < self.window_size and not self.fifo.empty():
                self.lock.acquire()
                self.window.append(self.fifo.get())
                self.lock.release()
                self.transmit_and_log(self.window[-1])

        
            

            

    def on_timeout(self):
        """
        Deals with the timeout condition
        """
        if self.timer.elapsed() > self.timeout:
            self.timer.restart()

        return True
    
    def init_window(self):
        """
        Initializes the window with the first N packets
        """
        self.lock.acquire()

        for _ in range(self.window_size):
            self.window.append(self.fifo.get())

        self.lock.release()

    def update_window(self, ack_seqnum):
        """
        Updates the window by removing the first packet and adding a new packet
        """
        self.lock.acquire()

        for i in range(len(self.window)):
            if self.window[i].seqnum == ack_seqnum:
                for _ in range(i):
                    self.window.pop(0)
                break

        self.lock.release()

    def init_fifo(self):
        """
        Initializes the fifo with all data packets
        """
        content = self.send_file.readlines()

        for i in range(len(content), self.data_size):
            pkt = Packet(1, i%32, self.data_size, content[i:i+self.data_size]) \
                if i+self.data_size < len(content) \
                else Packet(1, i%32, len(content)-i, content[i:])

            self.fifo.put(pkt)
        
    def send_syn(self):
        """
        Sends a SYN packet to the network emulator
        """
        self.send_sock.sendto(Packet(3, 0, 0, "").encode(), (self.ne_host, self.ne_port))
        self.seqnum_file.write('T=-1 SYN\n')


    def send_eot(self):
        """
        Sends an EOT packet to the network emulator
        """
        self.send_sock.sendto(Packet(2, 0, 0, "").encode(), (self.ne_host, self.ne_port))
        self.seqnum_file.write(f't={self.current_time} EOT\n')
        self.current_time += 1




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
    
