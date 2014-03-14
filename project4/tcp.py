import socket
import struct
import sys
import time
from random import randint

from ip import IPSocket
from utility import get_localhost_ip, get_open_port, checksum


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

TIME_OUT = 0.1


class TCPPacket:
    def __init__(self, src_ip='', src_port=0, dst_ip='', dst_port=80, data=''):
        self.src_port = src_port
        self.dst_port = dst_port
        self.seq_no = 0
        self.ack_no = 0
        self.doff = 5
        self.urg = 0
        self.psh = 0
        self.ack = 0
        self.rst = 0
        self.syn = 0
        self.fin = 0
        self.win_size = 4096
        self.check = 0
        self.urgent = 0
        self.data = data
        self.src_ip = src_ip
        self.dst_ip = dst_ip

    def reset(self):
        self.src_port = 0
        self.dst_port = 0
        self.seq_no = 0
        self.ack_no = 0
        self.doff = 5
        self.urg = 0
        self.psh = 0
        self.ack = 0
        self.rst = 0
        self.syn = 0
        self.fin = 0
        self.win_size = 6000
        self.check = 0
        self.urgent = 0
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
                                 self.seq_no,  # L: 4 Bytes
                                 self.ack_no,  # L
                                 offset_res,  # B
                                 flags,  # B
                                 self.win_size,  # H
                                 self.check,  # H
                                 self.urgent)  # H

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
                                 self.seq_no,  # L: 4 Bytes
                                 self.ack_no,  # L
                                 offset_res,  # B
                                 flags,  # B
                                 self.win_size) + \
                     struct.pack('H', self.check) + \
                     struct.pack('!H', self.urgent)

        return tcp_header + self.data

    def rebuild(self, raw_packet):
        # disassemble tcp header
        [self.src_port,
         self.dst_port,
         self.seq_no,
         self.ack_no,
         offset_res,
         flags,
         self.win_size] = struct.unpack('!HHIIBBH', raw_packet[0:16])
        [self.check] = struct.unpack('H', raw_packet[16:18])
        [self.urgent] = struct.unpack('!H', raw_packet[18:20])

        # get header length
        self.doff = offset_res >> 4

        # get flags
        self.fin = flags & 0x01
        self.syn = (flags & 0x02) >> 1
        self.rst = (flags & 0x04) >> 2
        self.psh = (flags & 0x08) >> 3
        self.ack = (flags & 0x10) >> 4
        self.urg = (flags & 0x20) >> 5

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
        print 'Sequence: %d\tAcknowledgement: %d' % (self.seq_no, self.ack_no)


class TCPSocket:
    def __init__(self):
        self.src_ip = ''
        self.src_port = 0
        self.des_ip = ''
        self.des_port = 0
        self.seq = 0
        self.ack = 0
        self.s = IPSocket()

        self.ack_count = 0
        self.pre_ack = -1
        self.pre_seq = -1

    def connect(self, des_host, des_port=80):

        self.des_ip = socket.gethostbyname(des_host)
        self.des_port = des_port

        self.src_ip = get_localhost_ip('eth0')
        self.src_port = get_open_port()

        # three way hand shake begins:
        self.seq = randint(0, 65535)
        packet = self.build_sending_packet()
        packet.syn = 1

        # Send SYN
        self.__send(self.src_ip, self.des_ip, packet)

        # receive syn+ack
        packet.reset()
        packet = self.__recv()
        print '[DEBUG]Connection Receive'
        packet.debug_print()
        if packet == '':
            sys.exit('Socket Time Out During Connection')
        if packet.ack_no == (self.seq + 1) and packet.syn == 1 and packet.ack == 1:
            self.ack = packet.seq_no + 1
            self.seq = packet.ack_no
        else:
            sys.exit('Wrong SYN+ACK Packet')

        # send ack
        packet = self.build_sending_packet()
        packet.ack = 1
        self.__send(self.src_ip, self.des_ip, packet)

    def send(self, _data):
        # Send the packet
        packet = self.build_sending_packet()
        packet.ack = 1
        packet.psh = 1
        packet.data = _data
        self.__send(self.src_ip, self.des_ip, packet)

        # Get ack of the sent packet
        packet.reset()
        packet = self.__recv()
        if packet == '':
            sys.exit('Socket Time Out During Sending TCP Packet')
        if packet.ack_no == (self.seq + len(_data)):
            self.ack = packet.seq_no + len(packet.data)
            self.seq = packet.ack_no
        else:
            sys.exit('Wrong ACK Packet')

    def recv(self):
        tcp_data = ''
        packet = TCPPacket()
        while True:
            if self.ack_count > 1:
                # send ack packet
                packet = self.build_sending_packet()
                # set ack to previous packet
                packet.ack_no = self.pre_ack
                packet.seq_np = self.pre_seq
                packet.ack = 1
                self.__send(self.src_ip, self.des_ip, packet)
                # after send ack, decrease ack_count by 1
                self.ack_count -= 1

            # recv packet
            packet.reset()
            packet = self.__recv()
            if packet == '':
                break
            # first set previous ack# to current ack
            if self.ack_count > 0:
                self.pre_ack = self.ack
                self.pre_seq = self.seq
            self.ack = packet.seq_no + len(packet.data)
            self.seq = packet.ack_no
            tcp_data += packet.data
            # add 1 to ack_count, for acknowledge
            self.ack_count += 1

        return tcp_data

    def close(self):
        # send fin+ack
        packet = self.build_sending_packet()
        packet.fin = 1
        if self.ack_count > 0:
            packet.ack = 1
        packet.psh = 1
        self.__send(self.src_ip, self.des_ip, packet)

        # recv fin+ack
        packet.reset()
        packet = self.__recv()
        if packet == '':
            sys.exit('Wrong FIN+ACK Packet')
        self.ack = packet.seq_no + 1
        self.seq = packet.ack_no

        'send ack'
        packet = self.build_sending_packet()
        packet.ack = 1
        self.__send(self.src_ip, self.des_ip, packet)

    def build_sending_packet(self):
        packet = TCPPacket()
        packet.src_port = self.src_port
        packet.dst_port = self.des_port
        packet.src_ip = self.src_ip
        packet.dst_ip = self.des_ip
        packet.seq_no = self.seq
        packet.ack_no = self.ack
        return packet

    def __send(self, src_ip, des_ip, packet):
        self.s.send(src_ip, des_ip, packet.build())
        print('[DEBUG]Send Packet:')
        packet.debug_print()

    def __recv(self):
        packet = TCPPacket()
        st_time = time.time()
        while (time.time() - st_time) < TIME_OUT:
            packet.reset()
            try:
                pkt = self.s.recv()
            except:
                continue
            # packet received
            packet.src_ip = self.des_ip
            packet.dst_ip = self.src_ip
            packet.rebuild(pkt)

            if packet.src_port == self.des_port and packet.dst_port == self.src_port:
                print '[DEBUG]Receive:'
                packet.debug_print()
                return packet
        return ''


if __name__ == "__main__":
    sock = TCPSocket()
    sock.connect('cs5700.ccs.neu.edu', 80)
    sock.close()
