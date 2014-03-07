import socket
import struct
import sys

from random import randint
from utility import checksum

'''
IP Header
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |Type of Service|          Total Length         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|      Fragment Offset    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Time to Live |    Protocol   |         Header Checksum       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Source Address                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Destination Address                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options                    |    Padding    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
'''

class IP_Packet:

    def __init__(self, source_ip, dest_ip, data = ''):
        # ip header fields
        self.ihl = 5 # IHL
        self.ver = 4 # Version
        self.tos = 0 # Type
        self.tot_len = 20 # Total length
        self.id = 0   #ID
        self.flag_df = 1 # 1 bit, Do Not Fragment
        self.flag_mf = 0 # 1 bit, More Fragments
        self.offset = 0
        self.ttl = 255   # Time to live
        self.proto = socket.IPPROTO_TCP  # protocol
        self.check = 0    # checksum
        self.src = socket.inet_aton(source_ip)
        self.dst = socket.inet_aton(dest_ip)
        self.data = data


    def create(self):
        self.id = randint(0, 65535)
        self.tot_len = self.ihl * 4 + len(self.data)

        # assemble header fileds without checksum
        header = struct.pack('!BBHHHBBH4s4s', \
         # the ! in the pack format string means network order
         (self.ver << 4) + self.ihl, # B: unsigned char, 1 Byte
         self.tos, # B
         self.tot_len, # H: unsigned short, 2 Bytes
         self.id, # H
         (((self.flag_df << 1) + self.flag_mf) << 13) + self.offset, # H
         self.ttl, # B
         self.proto, # B
         self.check, # H
         self.src, # 4s: 4 char[], 4 Bytes
         self.dst) # 4s

        # compute checksum and fill it
        self.check = checksum(header)

        header = struct.pack('!BBHHHBBH4s4s', \
         # the ! in the pack format string means network order
         (self.ver << 4) + self.ihl, # B: unsigned char, 1 Byte
         self.tos, # B
         self.tot_len, # H: unsigned short, 2 Bytes
         self.id, # H
         (((self.flag_df << 1) + self.flag_mf) << 13) + self.offset, # H
         self.ttl, # B
         self.proto, # B
         self.check, # H
         self.src, # 4s: 4 char[], 4 Bytes
         self.dst) # 4s

        return header + self.data

    def fragment(self):
        pass

    def reassemble(self):
        pass

    def printPacket(self):
        print('[DEBUG]The IP Packet\n')
        print 'Source: ' + str(self.src) +\
              ' Destination: ' + str(self.dst)

class IP_Socket:

    def __init__(self, src = '', dst = ''):
        self.src = src
        self.dst = dst
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        except socket.error, msg:
            print 'Socket could not be created. Error Message:' + msg[1]
            sys.exit()

    def send(self, src, dst, data):
        self.src = src
        self.dst = dst
        pack = IP_Packet(src, dst, data)
        self.sock.sendto(pack.create(), (dst, 0))

    def recv(self):
        packet, address = self.sock.recvfrom(1024)
        print('[DEBUG IP Recv]: From' + address + '\n' + packet)
        return packet

if __name__ == "__main__":
    pass

