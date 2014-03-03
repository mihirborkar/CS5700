import socket
import struct
from ip import IPSocket

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

class TCP_Packet:

    def __init__(self):
        # tcp header fields
        self.tcp_source = 1234   # source port
        self.tcp_dest = 80   # destination port
        self.tcp_seq = 0
        self.tcp_ack_seq = 0
        self.tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
        #tcp flags
        self.tcp_fin = 0
        self.tcp_syn = 1
        self.tcp_rst = 0
        self.tcp_psh = 0
        self.tcp_ack = 0
        self.tcp_urg = 0
        self.tcp_window = socket.htons (5840) #maximum allowed window size
        self.tcp_check = 0
        self.tcp_urg_ptr = 0

    def pack(self):
        tcp_offset_res = (self.tcp_doff << 4) + 0
        tcp_flags = self.tcp_fin + \
        (self.tcp_syn << 1) + \
        (self.tcp_rst << 2) + \
        (self.tcp_psh << 3) + \
        (self.tcp_ack << 4) + \
        (self.tcp_urg << 5)
        # the ! in the pack format string means network order
        self.tcp_header = struct.pack('!HHLLBBHHH' , \
        self.tcp_source, # H: 2 Bytes
        self.tcp_dest, # H
        self.tcp_seq, # L: 4 Bytes
        self.tcp_ack_seq, # L
        tcp_offset_res, # B
        tcp_flags,  # B
        self.tcp_window, # H
        self.tcp_check, # H
        self.tcp_urg_ptr) # H

    def toString(self):
        print('[DEBUG]The TCP Packet\n')

class TCPSocket:

    def __init__(self):
        sock = IPSocket()

    def connect(self):
        pass

    def close(self):
        pass

    def send(request):
        pass

    def recv():
        pass

if __name__ == "__main__":
    pass
