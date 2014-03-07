import socket
import struct
import time
from ip import *
from utility import get_localhost_IP, checksum
from random import randint

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

    def __init__(self, src_ip, src_port, dst_ip, dst_port = 80, data = ''):
        # tcp header fields
        self.src_port = src_port   # source port
        self.dst_port = dst_port   # destination port
        self.seq = 0  #sequence number
        self.ack_seq = 0  #acknowledge number
        self.doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
        #tcp flags
        self.fin = 0
        self.syn = 0
        self.rst = 0
        self.psh = 0
        self.ack = 0
        self.urg = 0
        self.window = 6000 #maximum allowed window size
        self.check = 0
        self.urg_ptr = 0
        self.data = data

        self.src_ip = socket.inet_aton(src_ip)
        self.dst_ip = socket.inet_aton(dst_ip)

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

        tcp_header = struct.pack('!HHLLBBHHH' , \
            self.src_port, # H: 2 Bytes
            self.dst_port, # H
            self.seq, # L: 4 Bytes
            self.ack_seq, # L
            offset_res, # B
            flags,  # B
            self.window, # H
            self.check, # H
            self.urg_ptr) # H

        # build a pseudo header for computing checksum
        pseudo_header = struct.pack('!4s4sBBH',
            self.src_ip,\
            self.dst_ip,\
            0, # Reserved byte
            socket.IPPROTO_TCP, # Protocol
            len(tcp_header) + len(self.data))
        pseudo_header = pseudo_header + tcp_header + self.data
        # Compute checksum
        self.check = checksum(pseudo_header)

        tcp_header = struct.pack('!HHLLBBHHH' , \
            self.src_port, # H: 2 Bytes
            self.dst_port, # H
            self.seq, # L: 4 Bytes
            self.ack_seq, # L
            offset_res, # B
            flags,  # B
            self.window, # H
            self.check, # H
            self.urg_ptr) # H

        return tcp_header + self.data

    def recreate(self, packet):
        # disassemble tcp header
        [self.src_port,\
         self.dst_port,\
         self.seq,\
         self.ack,\
         hlen,\
         flags,\
         self.window,\
         self.check,\
         self.urg_ptr] = struct.unpack('!HHIIBBHHH', packet[0:20])

        self.doff = hlen >> 4
        # get flags
        self.fin = flags & 0x01
        self.syn = (flags & 0x02) >> 1
        self.rst = (flags & 0x04) >> 2
        self.psh = (flags & 0x08) >> 3
        self.ack = (flags & 0x10) >> 4
        self.urg = (flags & 0x20) >> 5

        self.data = packet[self.doff * 4 :]

        tcp_header = struct.pack('!HHLLBBHHH' , \
            self.src_port, # H: 2 Bytes
            self.dst_port, # H
            self.seq, # L: 4 Bytes
            self.ack_seq, # L
            hlen, # B
            flags,  # B
            self.window, # H
            self.check, # H
            self.urg_ptr) # H

        # build a pseudo header for computing checksum
        pseudo_header = struct.pack('!4s4sBBH',
            self.src_ip,\
            self.dst_ip,\
            0, # Reserved byte
            socket.IPPROTO_TCP, # Protocol
            len(tcp_header) + len(self.data))
        pseudo_header = pseudo_header + tcp_header + self.data
        # Compute checksum
        self.check = checksum(pseudo_header)
        # Pack the header again
        tcp_header = struct.pack('!HHLLBBHHH' , \
            self.src_port, # H: 2 Bytes
            self.dst_port, # H
            self.seq, # L: 4 Bytes
            self.ack_seq, # L
            hlen, # B
            flags,  # B
            self.window, # H
            self.check, # H
            self.urg_ptr) # H

        return tcp_header + self.data

    def printPacket(self):
        print('[DEBUG]The TCP Packet\n')
        print 'Source Port : ' + str(self.src_port) +\
              ' Destination Port : ' + str(self.dst_port) +\
              ' Sequence Number : ' + str(self.seq) + \
              ' Acknowledgement : ' + str(self.ack_seq) + \
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

    def connect(self, hostname, port = 80):
        def get_open_port():
            '''Generate a free port'''
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', 0))
            port = s.getsockname()[1]
            s.close()
            return port

        self.dst_ip = socket.gethostbyname(hostname)
        self.dst_port = port
        self.src_ip = get_localhost_IP()
        self.src_port = get_open_port()
        # print '[DEBUG]Source Port:' + str(self.src_port)

        # Three-way handshake
        # Send SYN packet
        self.seq = randint(0, 65535)
        pack = self.build_packet('SYN')
        self.sock.send(self.src_ip, self.dst_ip, pack.create())

        #Receive SYN+ACK
        pack = self._raw_recv()
        print '[DEBUG] ACK Packet:\n' + repr(pack)
        if pack == '':
            sys.exit('Socket time out')
        if pack.ack == (self.seq + 1) and pack.syn == 1 and pack.ack == 1:
            self.ack = pack.seq + 1
            self.seq = pack.ack
        else:
            sys.exit('Wrong SYN+ACK Packet')

        # Send ACK
        pack = self.build_packet('ACK')
        self.sock.send(self.src_ip, self.dst_ip, pack.create())

    def close(self):
        # Four way tear down
        pass

    def send(self, request):
        pass

    def recv(self, buf_size):
        pass

    def _raw_recv(self):
        pack = TCP_Packet(self.src_ip, self.src_port,\
                        self.dst_ip, self.dst_port)
        start_time = time.time()
        while (time.time() - start_time) < TIME_OUT:
            p = self.sock.recv()
            pack.src_ip = self.dst_ip
            pack.dst_ip = self.src_ip
            pack.recreate(p)
            if pack.src_port == self.dst_port and pack.dst_port == self.src_port:
                return pack


    def build_packet(self, type):
        pack = TCP_Packet(self.src_ip, self.src_port,\
                        self.dst_ip, self.dst_port)
        pack.seq = self.seq
        pack.ack = self.ack
        if type == 'SYN':
            pack.syn = 1

        elif type == 'ACK':
            pack.ack = 1

        elif type == 'FIN':
            pack.fin = 1

        return pack

if __name__ == "__main__":
    sock = TCP_Socket()
    sock.connect('cs5700.ccs.neu.edu', 80)
