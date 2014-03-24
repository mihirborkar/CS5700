from random import randint
import socket
import struct
import sys
import time

from ip import IPSocket
from utility import ChecksumError, TimeOutError, get_localhost_ip, get_open_port, checksum


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
RTO = 2 * TIME_OUT


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
        self.win_size = 4096
        self.check = 0
        self.urgent = 0
        self.data = ''
        self.src_ip = ''
        self.dst_ip = ''

    def build(self):
        offset_res = (self.doff << 4) + 0
        self.check = 0

        flags = self.fin + \
                (self.syn << 1) + \
                (self.rst << 2) + \
                (self.psh << 3) + \
                (self.ack << 4) + \
                (self.urg << 5)

        # assemble tcp header without checksum
        tcp_header = struct.pack('!HHLLBBHHH',
                                 self.src_port,
                                 self.dst_port,
                                 self.seq_no,
                                 self.ack_no,
                                 offset_res,
                                 flags,
                                 self.win_size,
                                 self.check,
                                 self.urgent)

        # assemble pseudo header to calculate checksum
        pseudo_header = struct.pack('!4s4sBBH',
                                    socket.inet_aton(self.src_ip),
                                    socket.inet_aton(self.dst_ip),
                                    0,
                                    socket.IPPROTO_TCP,  # Protocol,
                                    self.doff * 4 + len(self.data))

        self.check = checksum(pseudo_header + tcp_header + self.data)

        # finally assemble tcp header
        tcp_header = struct.pack('!HHLLBBH',
                                 self.src_port,
                                 self.dst_port,
                                 self.seq_no,
                                 self.ack_no,
                                 offset_res,
                                 flags,
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
         self.win_size] = struct.unpack('!HHLLBBH', raw_packet[0:16])
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

        # get data
        self.data = raw_packet[self.doff * 4:]

        # assemble pseudo header to calculate checksum
        pseudo_header = struct.pack('!4s4sBBH',
                                    socket.inet_aton(self.src_ip),
                                    socket.inet_aton(self.dst_ip),
                                    0,
                                    socket.IPPROTO_TCP,  # Protocol,
                                    self.doff * 4 + len(self.data))
        if checksum(pseudo_header + raw_packet) != 0:
            raise ChecksumError('TCP')

    def debug_print(self):
        print '[DEBUG]TCP Packet'
        print 'Source: %s : %d' % (self.src_ip, self.src_port)
        print 'Destination: %s : %d' % (self.dst_ip, self.dst_port)
        print 'Sequence: %d\tAcknowledgement: %d\tLength: %d' % (self.seq_no, self.ack_no, len(self.data))
        print 'SYN: %d\tACK: %d\tPSH: %d\tFIN: %d' % (self.syn, self.ack, self.psh, self.fin)


class TCPSocket:
    def __init__(self):
        self.src_ip = ''
        self.src_port = 0
        self.dst_ip = ''
        self.dst_port = 0
        self.seq = 0
        self.ack = 0
        self.sock = IPSocket()

        self.ack_count = 0
        self.pre_ack = -1
        self.pre_seq = -1
        self.cwnd = 1

    def connect(self, dst_host, port=80):
        # Set field
        self.dst_ip = socket.gethostbyname(dst_host)
        self.dst_port = port

        self.src_ip = get_localhost_ip('eth0')
        self.src_port = get_open_port()

        # Update the IPSocket
        self.sock = IPSocket(self.src_ip, self.dst_ip)

        # three way hand shake
        self.seq = randint(0, 65535)
        packet = self.build_sending_packet()
        packet.syn = 1

        # Send SYN
        backup = packet
        self.__send(packet)

        # Receive SYN+ACK
        packet.reset()
        try:
            packet = self.__recv()
        except (ChecksumError, TimeOutError) as e:
            # print e
            self.cwnd -= 1
            self.__send(backup)

        if packet.ack_no == (self.seq + 1) and packet.syn == 1 and packet.ack == 1:
            self.ack = packet.seq_no + 1
            self.seq = packet.ack_no
            self.cwnd = 1000 if self.cwnd + 1 >= 1000 else self.cwnd + 1
        else:
            # print 'Wrong SYN+ACK Packet'
            self.cwnd -= 1
            self.__send(backup)

        # Send ACK
        packet = self.build_sending_packet()
        packet.ack = 1
        self.__send(packet)
        # print '===========Connection Done=========='

    def send(self, data):
        # Send the packet
        packet = self.build_sending_packet()
        packet.ack = 1
        packet.psh = 1
        packet.data = data
        backup = packet
        self.__send(packet)

        # Get ACK of the sent packet
        packet.reset()
        try:
            packet = self.__recv()
        except (ChecksumError, TimeOutError) as e:
            print e
            self.cwnd -= 1
            self.__send(backup)

        if packet.ack_no == (self.seq + len(data)):
            self.ack = packet.seq_no + len(packet.data)
            self.seq = packet.ack_no
            self.cwnd = 1000 if self.cwnd + 1 >= 1000 else self.cwnd + 1
        else:
            # print 'Wrong ACK Packet'
            self.cwnd -= 1
            self.__send(backup)

        # print '===========Send Done=========='

    def recv(self):
        tcp_data = ''
        packet = TCPPacket()
        while True:
            if self.ack_count > 1:
                # Send ACK packet
                packet = self.build_sending_packet()
                # Set ACK for previous packet
                packet.ack_no = self.pre_ack
                packet.seq_no = self.pre_seq
                packet.ack = 1
                self.__send(packet)
                # After sending ack, decrease ack_count by 1
                self.ack_count -= 1

            # Receive packet
            packet.reset()
            try:
                packet = self.__recv()
            except TimeOutError:
                break

            if packet.seq_no == self.ack:
                # print '~~~~~~~~~~~'
                # print packet.data
                # print '~~~~~~~~~~~'
                tcp_data += packet.data
            else:
                # Duplicate packets, drop it
                pass

            # Set previous ack# to current ack
            if self.ack_count > 0:
                self.pre_ack = self.ack
                self.pre_seq = self.seq
            self.ack = packet.seq_no + len(packet.data)
            self.seq = packet.ack_no
            self.cwnd = 1000 if self.cwnd + 1 >= 1000 else self.cwnd + 1
            # Increase ack_count by 1, for acknowledge
            self.ack_count += 1

        return tcp_data

    def close(self):
        # print '===========Close Begin=========='
        # Send FIN+ACK
        packet = self.build_sending_packet()
        packet.fin = 1
        if self.ack_count > 0:
            packet.ack = 1
        packet.psh = 1
        self.__send(packet)

        # Receive FIN+ACK
        packet.reset()
        try:
            packet = self.__recv()
        except (ChecksumError, TimeOutError) as e:
            print e

        self.ack = packet.seq_no + 1
        self.seq = packet.ack_no

        # send ack
        packet = self.build_sending_packet()
        packet.ack = 1
        self.__send(packet)
        # print '===========Close Done=========='

    def build_sending_packet(self):
        packet = TCPPacket()
        packet.src_port = self.src_port
        packet.dst_port = self.dst_port
        packet.src_ip = self.src_ip
        packet.dst_ip = self.dst_ip
        packet.seq_no = self.seq
        packet.ack_no = self.ack
        return packet

    def __send(self, packet):
        # print('[DEBUG]Send Packet:')
        # packet.debug_print()
        self.sock.send(packet.build())

    def __recv(self):
        packet = TCPPacket()
        st_time = time.time()
        while (time.time() - st_time) < TIME_OUT:
            packet.reset()
            try:
                pkt = self.sock.recv()
            except:
                continue
            # packet received
            packet.src_ip = self.dst_ip
            packet.dst_ip = self.src_ip
            packet.rebuild(pkt)

            if packet.src_port == self.dst_port and packet.dst_port == self.src_port:
                # print '[DEBUG]TCP Receive:'
                # packet.debug_print()
                return packet
        else:
            raise TimeOutError


if __name__ == "__main__":
    sock = TCPSocket()
    sock.connect('cs5700.ccs.neu.edu', 80)
    sock.close()
