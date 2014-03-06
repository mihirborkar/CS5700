import socket
import struct
from ip import *
from utility import get_IP_address
from random import randint

'''
TCP Header
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Acknowledgment Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Data |           |U|A|P|R|S|F|                               |
| Offset| Reserved  |R|C|S|S|Y|I|            Window             |
|       |           |G|K|H|T|N|N|                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |         Urgent Pointer        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options                    |    Padding    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             data                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
'''

# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0

    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        s = s + w

    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);

    #complement and mask to 4 byte short
    s = ~s & 0xffff

    return s

class TCP_Packet:

    def __init__(self, src_ip, src_port, dst_ip, dst_port = 80, data = ''):
        # tcp header fields
        self.source = src_port   # source port
        self.dest = dst_port   # destination port
        self.seq = 0  #sequence number
        self.ack_seq = 0  #acknowledge number
        self.doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
        #tcp flags
        self.fin = 0
        self.syn = 1
        self.rst = 0
        self.psh = 0
        self.ack = 0
        self.urg = 0
        self.window = socket.htons (5840) #maximum allowed window size
        self.check = 0
        self.urg_ptr = 0
        self.data = data

        self.src_ip = socket.inet_aton(src_ip)
        self.dst_ip = socket.inet_aton(dst_ip)

    def pack(self):
        # TCP data offset
        offset_res = (self.doff << 4) + 0
        # TCP flags
        flags = self.fin + \
        (self.syn << 1) + \
        (self.rst << 2) + \
        (self.psh << 3) + \
        (self.ack << 4) + \
        (self.urg << 5)
        # the ! in the pack format string means network order
        tcp_header = struct.pack('!HHLLBBHHH' , \
        self.source, # H: 2 Bytes
        self.dest, # H
        self.seq, # L: 4 Bytes
        self.ack_seq, # L
        offset_res, # B
        flags,  # B
        self.window, # H
        self.check, # H
        self.urg_ptr) # H

        # build a pseudo header to compute checksum
        pseudo_header = struct.pack('!4s4sBBH',
            self.src_ip,\
            self.dst_ip,\
            0, # Reserved byte
            socket.IPPROTO_TCP, # Protocol
            len(tcp_header) + len(self.data))

        pseudo_header = pseudo_header + tcp_header + self.data

        self.check = checksum(pseudo_header)

        tcp_header = struct.pack('!HHLLBBHHH' , \
        self.source, # H: 2 Bytes
        self.dest, # H
        self.seq, # L: 4 Bytes
        self.ack_seq, # L
        offset_res, # B
        flags,  # B
        self.window, # H
        self.check, # H
        self.urg_ptr) # H

        return tcp_header + self.data


    def toString(self):
        print('[DEBUG]The TCP Packet\n')
        print 'Source Port : ' + str(source_port) +\
              ' Dest Port : ' + str(dest_port) +\
              ' Sequence Number : ' + str(sequence) + \
              ' Acknowledgement : ' + str(acknowledgement) + \
              ' TCP header length : ' + str(tcph_length)

class TCPSocket:

    def __init__(self):
        self.src_ip = ''
        self.src_port = 0
        self.dst_ip = ''
        self.dst_port = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

    def connect(self, hostname, port = 80):
        self.dst_ip = socket.gethostbyname(hostname)
        self.dst_port = port
        self.src_ip = get_IP_address()
        self.src_port = 49472#randint(1024, 65535)
        # TODO: Check
        # Three way handshake
        pack1 = TCP_Packet(self.src_ip, self.src_port, self.dst_ip, self.dst_port)
        pack1.seq = 123
        self.sock.sendto(pack1.pack(), (self.dst_ip, self.dst_port))
        pack2 = self.sock.recvfrom(2048)
        print pack2
        # ack = pack2
        # pack3
        # self.sock.sendto(pack3)



    def close(self):
        # Four way tear down
        pass

    def send(request):
        pass

    def recv(buf_size):
        pass

if __name__ == "__main__":
    sock = TCPSocket()
    sock.connect('cs5700.ccs.neu.edu', 80)
