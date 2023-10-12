import os
import sys
import argparse
import socket
import math

from packet import Packet

# Writes the received content to file
def append_to_file(filename, data):
    file = open(filename, 'a')
    file.write(data)
    file.close()

def append_to_log(packet):
    """
    Appends the packet information to the log file
    """
    # raise NotImplementedError('append_to_log not implemented')
    return 
    

def send_ack(recv_packet: Packet, ne_addr: str, ne_port:str, socket: socket.socket): #Args to be added
    """
    Sends ACKs, EOTs, and SYN to the network emulator. and logs the seqnum.
    """
    
    if recv_packet.typ == 3:
        # Send SYNACK
        packet = Packet(3, 0, 0, "")
        s.sendto(packet.encode(), (ne_addr, ne_port))
        append_to_log(packet)




    # raise NotImplementedError('Send_ack not implemented')
    return True
    
if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser(description="Congestion Controlled GBN Receiver")
    parser.add_argument("ne_addr", metavar="<NE hostname>", help="network emulator's network address")
    parser.add_argument("ne_port", metavar="<NE port number>", help="network emulator's UDP port number")
    parser.add_argument("recv_port", metavar="<Receiver port number>", help="network emulator's network address")
    parser.add_argument("dest_filename", metavar="<Destination Filename>", help="Filename to store received data")

    args = parser.parse_args()
    ne_addr: str = args.ne_addr
    ne_port: int = int(args.ne_port)
    recv_port: int = int(args.recv_port)
    dest_filename: str = args.dest_filename

    # Clear the output and log files
    open(dest_filename, 'w').close()
    open('arrival.log', 'w').close()

    expected_seq_num = 0 # Current Expected sequence number
    seq_size = 32 # Max sequence number
    max_window_size = 10 # Max number of packets to buffer
    recv_buffer = {}  # Buffer to store the received data

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('', recv_port))  # Socket to receive data

        while True:
            # Receive packets, log the seqnum, and send response
            recv_packet, addr = s.recvfrom(1024)
            recv_packet = Packet(recv_packet)
            append_to_log(recv_packet)
            send_ack(recv_packet, ne_addr, ne_port, s)