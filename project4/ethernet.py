import binascii
import socket
import struct
import sys
from struct import pack
from utility import Packet, RawSocket, get_mac_address, get_gateway_ip, get_localhost_ip

'''
ARP Header
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        Hardware Type          |        Protocol Type          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Mac Addr len | Proto Addr len|       Operation Code          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   Sender Mac Address(0~3)                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Sender Mac Address(4~5)      |         Sender IP (0~1)       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Sender IP (2~3)     |  Target Mac Address(0~1)      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  Target Mac Address(2~5)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Targer IP                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
'''

ARPOP_REQUEST = 1
ARPOP_REPLY = 2


class EthernetPacket(Packet):

    def __init__(self, src, dst, proto=0x0800, data=''):
        Packet.__init__(self)

        self.src = src  # 6 Bytes
        self.dst = dst  # 6 Bytes
        self.type = proto  # 2 Bytes
        self.data = data

    def build(self):
        header = struct.pack('!6s6sH',
                             binascii.unhexlify(self.dst),
                             binascii.unhexlify(self.src),
                             self.type)
        return header + self.data

    def rebuild(self, raw_packet):
        [dst, src, self.type] = struct.unpack('!6s6sH', raw_packet[:14])
        self.dst = binascii.hexlify(dst)
        self.src = binascii.hexlify(src)
        self.data = raw_packet[14:]

    def debug_print(self):
        print('[DEBUG]Ethernet Packet')
        print 'From: %s\tTo: %s' % (self.src, self.dst)


class ARPPacket(Packet):

    def __init__(self, src_mac, src_ip, dst_mac, dst_ip, operation=ARPOP_REQUEST):
        Packet.__init__(self)

        self.htype = 0x0001  # ethernet
        self.ptype = 0x0800  # ip
        self.hlen = 6  # len(MAC address)
        self.plen = 4  # len(IP address)
        self.op = operation
        self.src_mac = src_mac
        self.src_ip = src_ip
        self.dst_mac = dst_mac
        self.dst_ip = dst_ip

    def build(self):
        arp = pack('!HHBBH6s4s6s4s',
                   self.htype,
                   self.ptype,
                   self.hlen,
                   self.plen,
                   self.op,
                   binascii.unhexlify(self.src_mac),
                   socket.inet_aton(self.src_ip),
                   binascii.unhexlify(self.dst_mac),
                   socket.inet_aton(self.dst_ip))
        return arp

    def rebuild(self, raw_packet):
        [self.htype,
         self.ptype,
         self.hlen,
         self.plen,
         self.op,
         src_mac,
         src_ip,
         dst_mac,
         dst_ip] = struct.unpack('!HHBBH6s4s6s4s', raw_packet)

        self.src_mac = binascii.hexlify(src_mac)
        self.src_ip = socket.inet_ntoa(src_ip)
        self.dst_mac = binascii.hexlify(dst_mac)
        self.dst_ip = socket.inet_ntoa(dst_ip)

    def debug_print(self):
        if self.op == ARPOP_REQUEST:
            print '[DEBUG]ARP Request:'
            print '%s @ %s request %s' % (self.src_mac, self.src_ip, self.dst_ip)
        if self.op == ARPOP_REPLY:
            print '[DEBUG]ARP Reply:'
            print '%s @ %s' % (self.src_mac, self.src_ip)


class EthernetSocket(RawSocket):
    def __init__(self):
        RawSocket.__init__(self)

        self.send_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
        self.send_sock.bind(('eth0', socket.SOCK_RAW))
        self.recv_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
        self.recv_sock.setblocking(0)

        self.src_mac = ''
        self.dst_mac = ''
        self.gateway_mac = ''

    def send(self, data=''):
        if self.gateway_mac == '':
            gateway_ip = get_gateway_ip()
            try:
                self.gateway_mac = self.find_mac(gateway_ip)
            except:
                sys.exit('ARP Request ' + gateway_ip + ' is Failed')

        # Set fields of Ethernet Packet
        self.src_mac = get_mac_address('eth0')
        self.dst_mac = self.gateway_mac
        packet = EthernetPacket(self.src_mac, self.gateway_mac, data=data)

        print '[DEBUG]Send Ethernet Packet'
        packet.debug_print()
        self.send_sock.send(packet.build())

    def recv(self):
        packet = EthernetPacket('', '')

        while True:
            pkt = self.recv_sock.recv(4096)
            packet.rebuild(pkt)
            if packet.dst == self.src_mac:  # and packet.src == self.dst_mac:
                return packet.data

    def find_mac(self, dst_ip):
        # Socket
        s_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
        r_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0806))
        r_sock.settimeout(1)

        # ARP Frame
        self.src_mac = get_mac_address('eth0')
        src_ip = get_localhost_ip('eth0')
        arp_req = ARPPacket(self.src_mac, src_ip, '000000000000', dst_ip)
        arp_req.debug_print()
        # Ethernet Frame
        packet = EthernetPacket(self.src_mac, 'ffffffffffff', 0x0806, arp_req.build())
        print('[DEBUG]Send Ethernet packet')
        packet.debug_print()

        # Send the ethernet frame
        s_sock.send(packet.build())

        arp_rep = ARPPacket('', '', '', '')
        while True:
            pkt = r_sock.recvfrom(4096)[0]
            packet.rebuild(pkt)

            if packet.dst == self.src_mac and packet.type == 0x0806:
                print('[DEBUG]ARP REPLY Ethernet Packet')
                packet.debug_print()
                arp_rep.rebuild((packet.data[:28]))
                arp_rep.debug_print()
                if arp_rep.src_ip == dst_ip and arp_rep.dst_ip == src_ip:
                    break
        s_sock.close()
        r_sock.close()

        return arp_rep.src_mac


if __name__ == '__main__':
    pass
