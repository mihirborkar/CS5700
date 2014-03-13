import socket
import struct
import sys
from ethernet import EthernetSocket
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


class IPPacket:
    def __init__(self, src_ip, dst_ip, data=''):
        # ip header fields
        self.ver = 4  # Version
        self.ihl = 5  # IHL
        self.tos = 0  # Type
        self.tot_len = 20  # Total length
        self.id = 0  # ID
        self.flag_df = 1  # 1 bit, Do Not Fragment
        self.flag_mf = 0  # 1 bit, More Fragments
        self.offset = 0
        self.ttl = 255  # Time to live
        self.proto = socket.IPPROTO_TCP  # protocol
        self.check = 0  # checksum
        self.src = src_ip
        self.dst = dst_ip
        self.data = data

    def reset(self):
        self.ver = 4  # Version
        self.ihl = 5  # IHL
        self.tos = 0  # Type
        self.tot_len = 20  # Total length
        self.id = 0  # ID
        self.flag_df = 1  # 1 bit, Do Not Fragment
        self.flag_mf = 0  # 1 bit, More Fragments
        self.offset = 0
        self.ttl = 255  # Time to live
        self.proto = socket.IPPROTO_TCP  # protocol
        self.check = 0  # checksum
        self.src = '0'
        self.dst = '0'
        self.data = ''

    def build(self):
        # Set fields
        self.id = randint(0, 65535)
        self.tot_len = self.ihl * 4 + len(self.data)

        # Assemble the header without the checksum
        header = struct.pack('!BBHHHBB',
                             (self.ver << 4) + self.ihl,  # B: unsigned char, 1 Byte
                             self.tos,  # B
                             self.tot_len,  # H: unsigned short, 2 Bytes
                             self.id,  # H
                             (((self.flag_df << 1) + self.flag_mf) << 13) + self.offset,  # H
                             self.ttl,  # B
                             self.proto) + \
                 struct.pack('H', self.check) + \
                 struct.pack('!4s4s', socket.inet_aton(self.src),  # 4s: 4 char[], 4 Bytes
                             socket.inet_aton(self.dst))  # 4s

        # Compute checksum
        self.check = checksum(header)

        # Reassemble the header with checksum
        header = struct.pack('!BBHHHBB',
                             (self.ver << 4) + self.ihl,  # B: unsigned char, 1 Byte
                             self.tos,  # B
                             self.tot_len,  # H: unsigned short, 2 Bytes
                             self.id,  # H
                             (((self.flag_df << 1) + self.flag_mf) << 13) + self.offset,  # H
                             self.ttl,  # B
                             self.proto) + \
                 struct.pack('H', self.check) + \
                 struct.pack('!4s4s', socket.inet_aton(self.src),  # 4s: 4 char[], 4 Bytes
                             socket.inet_aton(self.dst))  # 4s

        return header + self.data

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

        self.src = socket.inet_ntoa(src_ip)
        self.dst = socket.inet_ntoa(dst_ip)

        self.ver = (ver_ihl & 0xf0) >> 4
        self.ihl = ver_ihl & 0x0f
        self.flag_df = (flag_offset & 0x40) >> 14
        self.flag_mf = (flag_offset & 0x20) >> 13
        self.offset = flag_offset & 0x1f

        self.data = raw_packet[4 * self.ihl:self.tot_len]

        # Check the checksum
        header = raw_packet[:10] + struct.pack('H', 0) + raw_packet[12:self.ihl * 4]
        if checksum(header) == self.check:
            sys.exit('IP checksum does not match.')

    def debug_print(self):
        print '[DEBUG]IP Packet'
        print 'Source: %s\tDestination: %s\tChecksum: %X' % (self.src, self.dst, self.check)


class IPSocket:
    def __init__(self, src_ip, dst_ip):
        """
        Build the socket on Network layer
            :param src_ip: Source IP Address
            :param dst_ip: Destination IP Address
        """
        self.src = src_ip
        self.dst = dst_ip
        self.sock = EthernetSocket()

    def send(self, data=''):
        # Build the packet
        packet = IPPacket(self.src, self.dst, data)
        print '[DEBUG]Send IP Packet:'
        packet.debug_print()
        # Send the packet
        self.sock.send(packet.build())

    def recv(self):
        packet = IPPacket('0', '0')

        while True:
            packet.reset()
            pkt = self.sock.recv()
            packet.rebuild(pkt)

            print '[DEBUG]IP Receive:'
            packet.debug_print()

            if packet.proto == socket.IPPROTO_TCP and packet.src == self.dst and packet.dst == self.src:
                return packet.data


if __name__ == '__main__':
    pass
