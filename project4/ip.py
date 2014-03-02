import socket
import struct
import sys

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

class IP_Packet:

    def __init__(self, source_ip, dest_ip):
        # ip header fields
        self.ip_ihl = 5 # IHL
        self.ip_ver = 4 # Version
        self.ip_tos = 0 # Type
        self.ip_tot_len = 20 # Total length
        self.ip_id = 0   #ID
        self.ip_flag_df = 1
        self.ip_flag_mf = 0
        self.ip_offset = 0
        self.ip_ttl = 255   # Time to live
        self.ip_proto = socket.IPPROTO_TCP
        self.ip_check = 0    # checksum
        self.ip_saddr = socket.inet_aton(source_ip)
        self.ip_daddr = socket.inet_aton(dest_ip)


    def pack(self):
        # the ! in the pack format string means network order
        ip_header = pack('!BBHHHBBH4s4s', \
         (self.ip_ver << 4) + self.ip_ihl, \
         self.ip_tos, \
         self.ip_tot_len, \
         self.ip_id, \
         (((self.flag_df << 1) + self.flag_mf) << 13) + self.offset, \
         self.ip_ttl, \
         self.ip_proto, \
         self.ip_check, \
         self.ip_saddr, \
         self.ip_daddr)
        self.check = checksum(ip_header)

    def fragment(self):
        pass

    def reassemble(self):
        pass

    def toString(self):
        print('[DEBUG]The IP Packet\n')
