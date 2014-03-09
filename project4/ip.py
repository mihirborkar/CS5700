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

    def __init__(self, src_ip, dst_ip, data=''):
        # ip header fields
        self.ver = 4  # Version
        self.ihl = 5  # IHL
        self.tos = 0  # Type
        self.tot_len = 20  # Total length
        self.id = 0    # ID
        self.flag_df = 1  # 1 bit, Do Not Fragment
        self.flag_mf = 0  # 1 bit, More Fragments
        self.offset = 0
        self.ttl = 255    # Time to live
        self.proto = socket.IPPROTO_TCP   # protocol
        self.check = 0     # checksum
        self.src = socket.inet_aton(src_ip)
        self.dst = socket.inet_aton(dst_ip)
        self.data = data

    def reset(self):
        self.ver = 4  # Version
        self.ihl = 5  # IHL
        self.tos = 0  # Type
        self.tot_len = 20  # Total length
        self.id = 0    # ID
        self.flag_df = 1  # 1 bit, Do Not Fragment
        self.flag_mf = 0  # 1 bit, More Fragments
        self.offset = 0
        self.ttl = 255  # Time to live
        self.proto = socket.IPPROTO_TCP   # protocol
        self.check = 0  # checksum
        self.src = socket.inet_aton('0')
        self.dst = socket.inet_aton('0')
        self.data = ''

    def create(self):
        # Set fields
        self.id = randint(0, 65535)
        self.tot_len = self.ihl * 4 + len(self.data)

        # assemble header without checksum
        header = struct.pack('!BBHHHBBH4s4s',
                             (self.ver << 4) + self.ihl,   # B: unsigned char, 1 Byte
                             self.tos,   # B
                             self.tot_len,   # H: unsigned short, 2 Bytes
                             self.id,   # H
                             (((self.flag_df << 1) + self.flag_mf) << 13) + self.offset,   # H
                             self.ttl,   # B
                             self.proto,   # B
                             self.check,   # H
                             self.src,   # 4s: 4 char[], 4 Bytes
                             self.dst)  # 4s

        # Compute checksum
        self.check = checksum(header)

        # reassemble header with checksum
        header = struct.pack('!BBHHHBBH4s4s',
                             (self.ver << 4) + self.ihl,   # B: unsigned char, 1 Byte
                             self.tos,   # B
                             self.tot_len,   # H: unsigned short, 2 Bytes
                             self.id,   # H
                             (((self.flag_df << 1) + self.flag_mf) << 13) + self.offset,   # H
                             self.ttl,   # B
                             self.proto,   # B
                             self.check,   # H
                             self.src,   # 4s: 4 char[], 4 Bytes
                             self.dst)  # 4s

        return header + self.data

    def disassemble(self, raw_packet):

        [ver_ihl,
         self.tos,
         self.tot_len,
         self.id,
         flag_offset,
         self.ttl,
         self.proto,
         self.check,
         self.src,
         self.dst] = struct.unpack('!BBHHHBBH4s4s', raw_packet[0:20])

        self.ver = (ver_ihl & 0xf0) >> 4
        self.ihl = ver_ihl & 0x0f

        self.flag_df = (flag_offset & 0x40) >> 14
        self.flag_mf = (flag_offset & 0x20) >> 13
        self.offset = flag_offset & 0x1f

        self.data = raw_packet[4 * self.ihl:self.tot_len]

         # compare chksum
        header = raw_packet[:10] + struct.pack('H', 0) + raw_packet[12:self.ihl * 4]

        if checksum(header) != self.check:
            sys.exit('IP checksum does not match')

    def print_packet(self):
        print('[DEBUG]The IP Packet')
        print 'Source: ' + socket.inet_ntoa(self.src) +\
              ' Destination: ' + socket.inet_ntoa(self.dst)


class IP_Socket:

    def __init__(self, src_ip='', des_ip=''):
        self.src = src_ip
        self.des = des_ip
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

    def send(self, src_ip, des_ip, data=''):
        self.src = src_ip
        self.des = des_ip
        packet = IP_Packet(src_ip, des_ip, data)
        # send via network layer
        self.send_sock.sendto(packet.create(), (self.des, 0))
        print('[DEBUG] Send IP Packet:')
        packet.print_packet()

    def recv(self, timeout=0.5):
        packet = IP_Packet('0', '0')
        self.recv_sock.setblocking(0)

        while True:
            pkt = self.recv_sock.recv(2048)
            packet.disassemble(pkt)

            print('[DEBUG]IP Recv:')
            packet.print_packet()

            if packet.proto == socket.IPPROTO_TCP and packet.src == self.des and packet.dst == self.src:
                    return packet.data


if __name__ == '__main__':
    pass
