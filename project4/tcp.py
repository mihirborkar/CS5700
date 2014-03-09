from ip import IP_Socket
from random import randint
from utility import get_localhost_ip, checksum
import socket
import struct
import sys
import time

TIME_OUT = 1

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

    def __init__(self, src_ip, src_port, dst_ip, dst_port=80, data=''):
        # tcp header fields
        self.src_port = src_port   # source port
        self.dst_port = dst_port   # destination port
        self.seq = 0  # sequence number
        self.ack_seq = 0  # acknowledge number
        self.doff = 5    # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
        #tcp flags
        self.fin = 0
        self.syn = 0
        self.rst = 0
        self.psh = 0
        self.ack = 0
        self.urg = 0
        self.window = 6000  # maximum allowed window size
        self.check = 0
        self.urg_ptr = 0
        self.data = data

        self.src_ip = socket.inet_aton(src_ip)
        self.dst_ip = socket.inet_aton(dst_ip)

    def reset(self):
        # tcp header fields
        self.src_port = 0   # source port
        self.dst_port = 0  # destination port
        self.seq = 0  # sequence number
        self.ack_seq = 0  # acknowledge number
        self.doff = 5    # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
        # tcp flags
        self.fin = 0
        self.syn = 0
        self.rst = 0
        self.psh = 0
        self.ack = 0
        self.urg = 0
        self.window = 6000  # maximum allowed window size
        self.check = 0
        self.urg_ptr = 0
        self.data = ''
        self.src_ip = socket.inet_aton('0')
        self.dst_ip = socket.inet_aton('0')

    def create(self):
        # TCP data offset
        offset_res = (self.doff << 4) + 0
        # TCP flags
        flags = self.fin + \
                (self.syn << 1) + \
                (self.rst << 2) + \
                (self.psh << 3) + \
                (self.ack << 4) + \
                (self.urg << 5)

        tcp_header = struct.pack('!HHLLBBHHH',
                                 self.src_port,  # H: 2 Bytes
                                 self.dst_port,  # H
                                 self.seq,  # L: 4 Bytes
                                 self.ack_seq,  # L
                                 offset_res,  # B
                                 flags,  # B
                                 self.window,  # H
                                 self.check,  # H
                                 self.urg_ptr)  # H

        # build a pseudo header for computing checksum
        pseudo_header = struct.pack('!4s4sBBH',
                                    self.src_ip,
                                    self.dst_ip,
                                    0,  # Reserved byte
                                    socket.IPPROTO_TCP,  # Protocol
                                    len(tcp_header) + len(self.data))
        pseudo_header = pseudo_header + tcp_header + self.data

        # Compute checksum
        self.check = checksum(pseudo_header)

        tcp_header = struct.pack('!HHLLBBHHH',
                                 self.src_port,  # H: 2 Bytes
                                 self.dst_port,  # H
                                 self.seq,  # L: 4 Bytes
                                 self.ack_seq,  # L
                                 offset_res,  # B
                                 flags,  # B
                                 self.window,  # H
                                 self.check,  # H
                                 self.urg_ptr)  # H

        return tcp_header + self.data

    def disassemble(self, raw_packet):
    # disassemble tcp header
        [self.src_port,
         self.dst_port,
         self.seq,
         self.ack,
         offset_res,
         flags,
         self.window,
         self.check,
         self.urg_ptr] = struct.unpack('!HHLLBBHHH', raw_packet[0:20])

        self.doff = offset_res >> 4
        # get flags
        self.fin = flags & 0x01
        self.syn = (flags & 0x02) >> 1
        self.rst = (flags & 0x04) >> 2
        self.psh = (flags & 0x08) >> 3
        self.ack = (flags & 0x10) >> 4
        self.urg = (flags & 0x20) >> 5

        self.data = raw_packet[4 * self.doff:]

        tcp_header = struct.pack('!HHLLBBHHH',
                                 self.src_port,  # H: 2 Bytes
                                 self.dst_port,  # H
                                 self.seq,  # L: 4 Bytes
                                 self.ack_seq,  # L
                                 offset_res,  # B
                                 flags,  # B
                                 self.window,  # H
                                 self.check,  # H
                                 self.urg_ptr)  # H

        # build a pseudo header for computing checksum
        pseudo_header = struct.pack('!4s4sBBH',
                                    self.src_ip,
                                    self.dst_ip,
                                    0,  # Reserved byte
                                    socket.IPPROTO_TCP,  # Protocol
                                    len(tcp_header) + len(self.data))
        pseudo_header = pseudo_header + tcp_header + self.data

        # Compute checksum
        self.check = checksum(pseudo_header)

        tcp_header = struct.pack('!HHLLBBHHH',
                                 self.src_port,  # H: 2 Bytes
                                 self.dst_port,  # H
                                 self.seq,  # L: 4 Bytes
                                 self.ack_seq,  # L
                                 offset_res,  # B
                                 flags,  # B
                                 self.window,  # H
                                 self.check,  # H
                                 self.urg_ptr)  # H

        return tcp_header + self.data

    def print_packet(self):
        print('[DEBUG]The TCP Packet')
        print 'Source Port : ' + str(self.src_port) +\
              ' Source IP : ' + socket.inet_ntoa(self.src_ip) +\
              ' Destination Port : ' + str(self.dst_port) +\
              ' Destination IP : ' + socket.inet_ntoa(self.dst_ip) +\
              ' Sequence Number : ' + str(self.seq) +\
              ' Acknowledgement : ' + str(self.ack_seq) +\
              ' TCP header length : ' + str(self.doff * 4)


class TCP_Socket:

    def __init__(self):
        self.src_ip = ''
        self.src_port = 0
        self.dst_ip = ''
        self.dst_port = 0
        self.seq = 0
        self.ack = 0
        self.sock = IP_Socket()

        self.my_stamp = 0
        self.echo_stamp = 0
        self.last_time = 0

        self.ack_count = 0
        self.pre_ack = -1
        self.pre_seq = -1

    def connect(self, dst_addr, dst_port=80):
        self.dst_ip = socket.gethostbyname(dst_addr)
        self.dst_port = dst_port
        self.src_ip = get_localhost_ip()
        self.src_port = self.get_open_port()

        # three way hand shake
        self.seq = randint(0, 65535)
        packet = self.build_sending_packet()
        packet.syn = 1

        # Send SYN
        self._send(self.src_ip, self.dst_ip, packet)

        # Receive SYN + ACK
        packet.reset()
        packet = self._recv()
        print('[DEBUG] Connect recv')
        print repr(packet.data)
        if packet == '':
            sys.exit('Socket Time Out During Connection')
        if packet.ack_seq == (self.seq + 1) and packet.syn == 1 and packet.ack == 1:
            self.ack = packet.seq + 1
            self.seq = packet.ack_seq
        else:
            sys.exit('Wrong SYN+ACK Packet')

        # Send ACK
        packet = self.build_sending_packet()
        packet.ack = 1
        self._send(self.src_ip, self.dst_ip, packet)

    def send(self, data):
        # Build the packet
        packet = self.build_sending_packet()
        packet.ack = 1
        packet.psh = 1
        packet.data = data

        self._send(self.src_ip, self.dst_ip, packet)

        # Receive ACK
        packet.reset()
        packet = self._recv()
        if packet == '':
            sys.exit('Socket Time Out During Sending TCP Packet')
        if packet.ack_seq == (self.seq + len(data)):
            self.ack = packet.seq + len(packet.data)
            self.seq = packet.ack_seq
        else:
            sys.exit('Wrong ACK Packet')

    def recv(self):
        tcp_data = ''
        packet = TCP_Packet('0', 0, '0')
        while True:
            if self.ack_count > 1:
                # Send ACK
                packet = self.build_sending_packet()
                # set ack for previous packet
                packet.ack_seq = self.pre_ack
                packet.seq = self.pre_seq
                packet.ack = 1
                self._send(self.src_ip, self.dst_ip, packet)
                # Decrease ack_count by 1 after finishing send ACK
                self.ack_count -= 1

            # Receive
            packet.reset()
            packet = self._recv()
            if packet == '':
                break
            # Set previous ack as current ack
            if self.ack_count > 0:
                self.pre_ack = self.ack
                self.pre_seq = self.seq

            self.ack = packet.seq + len(packet.data)
            self.seq = packet.ack_seq
            tcp_data += packet.data
            # Increase ack_count by 1 after finishing acknowledge
            self.ack_count += 1

        return tcp_data

    def close(self):
        # Send FIN + ACK
        packet = self.build_sending_packet()
        packet.fin = 1
        if self.ack_count > 0:
            packet.ack = 1
        packet.psh = 1
        self._send(self.src_ip, self.dst_ip, packet)

        # Receive FIN + ACK
        packet.reset()
        packet = self._recv()
        if packet == '':
            sys.exit('Wrong FIN+ACK Packet')
        self.ack = packet.seq + 1
        self.seq = packet.ack_seq

        # Send ACK
        packet = self.build_sending_packet()
        packet.ack = 1
        self._send(self.src_ip, self.dst_ip, packet)

    def build_sending_packet(self):
        packet = TCP_Packet(self.src_ip, self.src_port, self.dst_ip, self.dst_port)
        packet.seq = self.seq
        packet.ack_seq = self.ack
        return packet

    def get_open_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def _send(self, src_ip, des_ip, packet):
        print('[DEBUG]Send Packet:')
        packet.print_packet()

        self.sock.send(src_ip, des_ip, packet.create())

    def _recv(self):
        packet = TCP_Packet('0', 0, '0')
        start_time = time.time()
        while (time.time() - start_time) < TIME_OUT:
            packet.reset()
            pkt = self.sock.recv()

            packet.src_ip = self.dst_ip
            packet.dst_ip = self.src_ip
            packet.disassemble(pkt)
            #print 'recv:'
            #packet.print_packet()
            if packet.src_port == self.dst_port and packet.dst_port == self.src_port:
                return packet
        return ''


if __name__ == "__main__":
    sock = TCP_Socket()
    sock.connect('cs5700.ccs.neu.edu', 80)
