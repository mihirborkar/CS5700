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
        self.ip_id = 54321   #ID
        self.ip_flag_df = 1
        self.ip_flag_mf = 0
        self.ip_offset = 0
        self.ip_ttl = 255   # Time to live
        self.ip_proto = socket.IPPROTO_TCP  # protocol
        self.ip_check = 0    # checksum
        self.ip_saddr = socket.inet_aton(source_ip)
        self.ip_daddr = socket.inet_aton(dest_ip)


    def pack(self):
        ip_header = struct.pack('!BBHHHBBH4s4s', \
         # the ! in the pack format string means network order
         (self.ip_ver << 4) + self.ip_ihl, # B: unsigned char, 1 Byte
         self.ip_tos, # B
         self.ip_tot_len, # H: unsigned short, 2 Bytes
         self.ip_id, # H
         (((self.flag_df << 1) + self.flag_mf) << 13) + self.offset, # H
         self.ip_ttl, # B
         self.ip_proto, # B
         self.ip_check, # H
         self.ip_saddr, # 4s: 4 char[], 4 Bytes
         self.ip_daddr) # 4s
        # compute checksum and fill it
        self.check = checksum(ip_header)

    def fragment(self):
        pass

    def reassemble(self):
        pass

    def toString(self):
        print('[DEBUG]The IP Packet\n')

class IPSocket:

    def __init__(self):
        pass

    def send(self, request):
        pass

    def recv(self, request):
        pass

if __name__ == "__main__":
    pass
# #create a raw socket
# try:
#     s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
# except socket.error , msg:
#     print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
#     sys.exit()

# # tell kernel not to put in headers, since we are providing it
# s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
