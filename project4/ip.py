from random import randint
import socket
import struct

from ethernet import EthernetSocket
from utility import ChecksumError, checksum


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


class IPPacket:
    def __init__(self, src='', dst='', data=''):
        self.ver = 4
        self.ihl = 5
        self.tos = 0
        self.tot_len = 20
        self.id = 0
        self.flag_df = 1
        self.flag_mf = 0
        self.offset = 0
        self.ttl = 255
        self.proto = socket.IPPROTO_TCP
        self.check = 0
        self.src = src
        self.dst = dst
        self.data = data

    def reset(self):
        self.ver = 4
        self.ihl = 5
        self.tos = 0
        self.tot_len = 20
        self.id = 0
        self.flag_df = 1
        self.flag_mf = 0
        self.offset = 0
        self.ttl = 255
        self.proto = socket.IPPROTO_TCP
        self.check = 0
        self.src = 0
        self.dst = 0
        self.data = ''

    def build(self):
        self.id = randint(0, 65535)
        self.tot_len = self.ihl * 4 + len(self.data)
        src_ip = socket.inet_aton(self.src)
        dst_ip = socket.inet_aton(self.dst)

        # assemble header without checksum
        ip_header = struct.pack('!BBHHHBBH4s4s',
                                (self.ver << 4) + self.ihl,
                                self.tos,
                                self.tot_len,
                                self.id,
                                (((self.flag_df << 1) + self.flag_mf) << 13) + self.offset,
                                self.ttl,
                                self.proto,
                                self.check,
                                src_ip,
                                dst_ip)

        self.check = checksum(ip_header)

        # reassemble header with checksum
        ip_header_new = struct.pack('!BBHHHBB',
                                    (self.ver << 4) + self.ihl,
                                    self.tos,
                                    self.tot_len,
                                    self.id,
                                    (((self.flag_df << 1) + self.flag_mf) << 13) + self.offset,
                                    self.ttl,
                                    self.proto) + \
                        struct.pack('H', self.check) + \
                        struct.pack('!4s4s', src_ip, dst_ip)

        packet = ip_header_new + self.data

        return packet

    def rebuild(self, raw_packet):
        [ver_ihl,
         self.tos,
         self.tot_len,
         self.id,
         flag_offset,
         self.ttl,
         self.proto] = struct.unpack('!BBHHHBB', raw_packet[0:10])
        [self.check] = struct.unpack('H', raw_packet[10:12])
        [src_ip, dst_ip] = struct.unpack('!4s4s', raw_packet[12:20])

        self.ver = (ver_ihl & 0xf0) >> 4
        self.ihl = ver_ihl & 0x0f

        self.flag_df = (flag_offset & 0x40) >> 14
        self.flag_mf = (flag_offset & 0x20) >> 13
        self.offset = flag_offset & 0x1f

        self.src = socket.inet_ntoa(src_ip)
        self.dst = socket.inet_ntoa(dst_ip)

        self.data = raw_packet[self.ihl * 4:self.tot_len]

        # Check the checksum
        header = raw_packet[:self.ihl * 4]

        if checksum(header) != 0:
            raise ChecksumError('IP')

    def debug_print(self):
        print '[DEBUG]IP Packet'
        print 'Source: %s\tDestination: %s' % (self.src, self.dst)


class IPSocket:
    def __init__(self, src_ip='', dst_ip=''):
        self.src = src_ip
        self.dst = dst_ip

        # self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        #self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        #self.recv_sock.setblocking(0)

        self.sock = EthernetSocket()

    def send(self, data):

        packet = IPPacket(self.src, self.dst, data)
        # print '[DEBUG]Send IP Packet:'
        # packet.debug_print()
        # self.send_s.sendto(packet.build(), (self.des, 0))
        self.sock.send(packet.build())

    def recv(self):
        packet = IPPacket()
        while True:
            packet.reset()
            # pkt = self.recv_sock.recv(4096)
            pkt = self.sock.recv()
            packet.rebuild(pkt)

            # print '[DEBUG]IP Receive:'
            # packet.debug_print()

            if packet.proto == socket.IPPROTO_TCP and packet.src == self.dst and packet.dst == self.src:
                return packet.data


if __name__ == '__main__':
    pass
