from ip import IPSocket
from random import randint
from utility import Packet, RawSocket, get_localhost_ip, get_open_port, checksum
import binascii
import socket
import struct
import sys
import time

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

TIME_OUT = 1


class TCPPacket(Packet):

    def __init__(self, src_ip, src_port, dst_ip, dst_port=80, data=''):
        Packet.__init__(self)

        self.src_port = src_port  # source port
        self.dst_port = dst_port  # destination port
        self.seqno = 0  # sequence number
        self.ackno = 0  # acknowledge number
        self.doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
        self.fin = 0
        self.syn = 0
        self.rst = 0
        self.psh = 0
        self.ack = 0
        self.urg = 0
        self.winsize = 4096  # maximum allowed window size
        self.check = 0
        self.urg_ptr = 0
        self.data = data
        self.src_ip = src_ip  # source ip address
        self.dst_ip = dst_ip  # destination ip address

    def reset(self):
        # tcp header fields
        self.src_port = 0   # source port
        self.dst_port = 0  # destination port
        self.seqno = 0  # sequence number
        self.ackno = 0  # acknowledge number
        self.doff = 5    # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
        # tcp flags
        self.fin = 0
        self.syn = 0
        self.rst = 0
        self.psh = 0
        self.ack = 0
        self.urg = 0
        self.winsize = 4096  # maximum allowed window size
        self.check = 0
        self.urg_ptr = 0
        self.data = ''
        self.src_ip = '0'
        self.dst_ip = '0'

    def build(self):
        # TCP data offset
        offset_res = (self.doff << 4) + 0
        # TCP flags
        flags = self.fin + \
                (self.syn << 1) + \
                (self.rst << 2) + \
                (self.psh << 3) + \
                (self.ack << 4) + \
                (self.urg << 5)
        src_ip = socket.inet_aton(self.src_ip)
        dst_ip = socket.inet_aton(self.dst_ip)

        tcp_header = struct.pack('!HHLLBBHHH',
                                 self.src_port,  # H: 2 Bytes
                                 self.dst_port,  # H
                                 self.seqno,  # L: 4 Bytes
                                 self.ackno,  # L
                                 offset_res,  # B
                                 flags,  # B
                                 self.winsize,  # H
                                 self.check,  # H
                                 self.urg_ptr)  # H

        # build a pseudo header for computing checksum
        pseudo_header = struct.pack('!4s4sBBH',
                                    src_ip,
                                    dst_ip,
                                    0,  # Reserved byte
                                    socket.IPPROTO_TCP,  # Protocol
                                    len(tcp_header) + len(self.data))

        # Compute checksum
        self.check = checksum(pseudo_header + tcp_header + self.data)

        # checksum is NOT in network byte order
        tcp_header = struct.pack('!HHLLBBH',
                                 self.src_port,  # H: 2 Bytes
                                 self.dst_port,  # H
                                 self.seqno,  # L: 4 Bytes
                                 self.ackno,  # L
                                 offset_res,  # B
                                 flags,  # B
                                 self.winsize) + \
                     struct.pack('H', self.check) + \
                     struct.pack('!H', self.urg_ptr)

        return tcp_header + self.data

    def rebuild(self, raw_packet):
        # disassemble tcp header
        [self.src_port,
         self.dst_port,
         self.seqno,
         self.ackno,
         offset_res,
         flags,
         self.winsize] = struct.unpack('!HHLLBBH', raw_packet[0:16])
        self.check = struct.unpack('H', raw_packet[16:18])
        self.urg_ptr = struct.unpack('!H', raw_packet[18:20])

        self.doff = offset_res >> 4
        # get flags
        self.fin = flags & 0x01
        self.syn = (flags & 0x02) >> 1
        self.rst = (flags & 0x04) >> 2
        self.psh = (flags & 0x08) >> 3
        self.ack = (flags & 0x10) >> 4
        self.urg = (flags & 0x20) >> 5

        self.data = raw_packet[4 * self.doff:]

        # TODO: Check checksum

    def debug_print(self):
        print '[DEBUG]TCP Packet'
        print 'Source: %s : %d' % (self.src_ip, self.src_port)
        print 'Destination: %s : %d' % (self.dst_ip, self.dst_port)
        print 'Sequence: %d\tAcknowledgement: %d\nHeader Length: %d\tChecksum: %X' % \
              (self.seqno, self.ackno, self.doff * 4, self.check)

    def debug_print_hex(self):
        print binascii.hexlify(self.build())


class TCPSocket(RawSocket):

    def __init__(self):
        RawSocket.__init__(self)
        self.src_ip = '0'
        self.src_port = 0
        self.dst_ip = '0'
        self.dst_port = 0
        self.seq = 0
        self.ack = 0
        self.sock = IPSocket(self.src_ip, self.dst_ip)

        self.ack_count = 0
        self.pre_ack = -1
        self.pre_seq = -1

    def connect(self, dst_host, dst_port=80):
        self.dst_ip = socket.gethostbyname(dst_host)
        self.dst_port = dst_port
        self.src_ip = get_localhost_ip()
        self.src_port = get_open_port()

        self.sock = IPSocket(self.src_ip, self.dst_ip)

        # three way hand shake
        self.seq = randint(0, 65535)
        packet = self.build_sending_packet()
        packet.syn = 1

        # Send SYN
        self.__send(packet)

        # Receive SYN + ACK
        packet.reset()
        packet = self.__recv()
        print '[DEBUG]Connection Receive'
        packet.debug_print()
        if packet == '':
            sys.exit('Socket Time Out During Connection')
        if packet.ackno == (self.seq + 1) and packet.syn == 1 and packet.ack == 1:
            self.ack = packet.seqno + 1
            self.seq = packet.ackno
        else:
            sys.exit('Wrong SYN+ACK Packet')

        # Send ACK
        packet = self.build_sending_packet()
        packet.ack = 1
        self.__send(packet)

    def send(self, data):
        # Build the packet
        packet = self.build_sending_packet()
        packet.ack = 1
        packet.psh = 1
        packet.data = data

        # Send the packet
        self.__send(packet)

        # Receive ACK
        packet.reset()
        packet = self.__recv()
        if packet == '':
            sys.exit('Socket Time Out During Sending TCP Packet')
        if packet.ackno == (self.seq + len(data)):
            self.ack = packet.seqno + len(packet.data)
            self.seq = packet.ackno
        else:
            sys.exit('Wrong ACK Packet')

    def recv(self):
        total_data = []
        packet = TCPPacket('0', 0, '0')
        while True:
            if self.ack_count > 1:
                # Send ACK
                packet = self.build_sending_packet()
                # Set ack for previous packet
                packet.ackno = self.pre_ack
                packet.seqno = self.pre_seq
                packet.ack = 1
                self.__send(packet)
                # Decrease ack_count by 1 after finishing send ACK
                self.ack_count -= 1

            # Receive
            packet.reset()
            pkt = self.__recv()
            if pkt == '':
                break
            # Set previous ack as current ack
            if self.ack_count > 0:
                self.pre_ack = self.ack
                self.pre_seq = self.seq

            packet.rebuild(pkt)
            self.ack = packet.seqno + len(packet.data)
            self.seq = packet.ackno
            total_data.append(packet.data)
            # Increase ack_count by 1 after finishing acknowledge
            self.ack_count += 1

        return ''.join(total_data)

    def close(self):
        # Send FIN + ACK
        packet = self.build_sending_packet()
        packet.fin = 1
        if self.ack_count > 0:
            packet.ack = 1
        packet.psh = 1
        self.__send(packet)

        # Receive FIN + ACK
        packet.reset()
        pkt = self.__recv()
        if pkt == '':
            sys.exit('Wrong FIN+ACK Packet')
        packet.rebuild(pkt)
        self.ack = packet.seqno + 1
        self.seq = packet.ackno

        # Send ACK
        packet = self.build_sending_packet()
        packet.ack = 1
        self.__send(packet)

    def build_sending_packet(self):
        packet = TCPPacket(self.src_ip, self.src_port, self.dst_ip, self.dst_port)
        packet.seqno = self.seq
        packet.ackno = self.ack
        return packet

    def __send(self, packet):
        print('[DEBUG]Send Packet:')
        packet.debug_print_hex()
        packet.debug_print()

        self.sock.send(packet.build())

    def __recv(self):
        packet = TCPPacket('0', 0, '0')
        start_time = time.time()

        while (time.time() - start_time) < TIME_OUT:
            packet.reset()

            # Receive
            pkt = self.sock.recv()
            packet.rebuild(pkt)

            if packet.src_port == self.dst_port and packet.dst_port == self.src_port:
                # print '[DEBUG]Receive:'
                # packet.debug_print()
                return packet
        return ''


if __name__ == "__main__":
    sock = TCPSocket()
    sock.connect('cs5700.ccs.neu.edu', 80)
