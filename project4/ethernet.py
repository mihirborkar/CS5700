import socket
import struct
import sys
from struct import pack
import binascii
from utility import get_mac_address, get_gateway_ip, get_localhost_ip

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


class Ethernet_Packet:

    def __init__(self, data=''):
        self.src = pack('!6B', *(0x00,)*6)
        self.dst = pack('!6B', *(0x00,)*6)
        self.type = 0
        self.data = data
        
    def create(self, proto=0x0800):
        dst = binascii.unhexlify(self.dst)
        src = binascii.unhexlify(self.src)
        self.type = proto

        header = struct.pack('!6s6sH', dst, src, self.type)

        return header + self.data
    
    def recreate(self, raw_packet):
        [dst, src, self.type] = struct.unpack('!6s6sH', raw_packet[:14])
        self.data = raw_packet[14:]
        self.dst = dst
        self.src = src
        
    def print_packet(self):
        print('[DEBUG]Print Ethernet Packet')
        print('From:' + self.src + '\tTo:' + self.dst)


class ARP_Packet:

    def __init__(self):
        self.htype = 0x0001  # ethernet
        self.ptype = 0x0800  # ip
        self.hlen = 6  # len(MAC address)
        self.plen = 4  # len(IP address)
        self.op = 0
        self.src_mac = ''
        self.src_ip = ''
        self.dst_mac = ''
        self.dst_ip = ''
        
    def create(self, opeartion=ARPOP_REQUEST):
        self.op = opeartion
        src_mac = binascii.unhexlify(self.src_mac)
        src_ip = socket.inet_aton(self.src_ip)
        dst_mac = binascii.unhexlify(self.dst_mac)
        dst_ip = socket.inet_aton(self.dst_ip)
        arpfram = pack('!HHBBH6s4s6s4s',
                       self.htype,
                       self.ptype,
                       self.hlen,
                       self.plen,
                       self.op,
                       src_mac,
                       src_ip,
                       dst_mac,
                       dst_ip)
        return arpfram

    def recreate(self, raw_packet):
        [self.htype, self.ptype, self.hlen, self.plen, self.op,
         src_mac, src_ip, dst_mac, dst_ip] = struct.unpack('!HHBBH6s4s6s4s', raw_packet)

        self.src_mac = binascii.hexlify(src_mac)
        self.src_ip = socket.inet_ntoa(src_ip)
        self.dst_mac = binascii.hexlify(dst_mac)
        self.dst_ip = socket.inet_ntoa(dst_ip)

    def print_packet(self):
        if self.op == ARPOP_REQUEST:
            print('[DEBUG] ARP Request:')
            print '%s Request %s' % (self.src_ip, self.dst_ip)
        if self.op == ARPOP_REPLY:
            print('[DEBUG] ARP Reply:')
            print '%s\'s Address: %s' % (self.src_ip, self.src_mac)


class Ethernet_Socket:
    def __init__(self):
        self.send_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
        self.send_sock.bind(('eth0', socket.SOCK_RAW))
        
        self.recv_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
        self.recv_sock.setblocking(0)

        self.src_mac = ''
        self.dst_mac = ''

        self.gateway_mac = ''
        
    def send(self, data=''):
        packet = Ethernet_Packet()
        if self.gateway_mac == '':
            gateway_ip = get_gateway_ip()
            try:
                self.gateway_mac = self.find_mac(gateway_ip)
            except:
                sys.exit('ARP Request Failed')

        # Set fields of Ethernet Packet
        packet.dst = self.gateway_mac
        self.dst_mac = packet.dst
        packet.src = self.src_mac
        packet.data = data

        self.send_sock.send(packet.create())

    def recv(self):
        packet = Ethernet_Packet()

        while True:
            pkt = self.recv_sock.recvfrom(6000)[0]
            packet.recreate(pkt)
            if packet.dst == self.src_mac:  # and packet.src == self.dst_mac:
                return packet.data
        
    def find_mac(self, dst_ip):
        s_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
        r_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
        r_sock.settimeout(1)
        
        self.src_mac = get_mac_address('eth0')
        src_ip = get_localhost_ip('eth0')
        arp_req = ARP_Packet()
        # Set fields of ARP Packet
        arp_req.src_mac = self.src_mac
        arp_req.src_ip = src_ip
        arp_req.dst_mac = '000000000000'
        arp_req.dst_ip = dst_ip

        packet = Ethernet_Packet()
        packet.dst = 'ffffffffffff'
        packet.src_mac = self.src_mac
        packet.data = arp_req.create()

        s_sock.sendto(packet.create(), ('eth0', 0))

        arp_rep = ARP_Packet()
        while True:
            pkt = r_sock.recvfrom(4096)[0]
            packet.recreate(pkt)

            print('[DEBUG] ARP REPLY Ethernet Packet')
            packet.print_packet()

            if packet.dst == self.src_mac:
                arp_rep.recreate(packet.data[:28])
                print('[DEBUG] ARP REPLY')
                arp_rep.print_packet()
                if arp_rep.src_ip == dst_ip and arp_rep.dst_ip == src_ip:
                    break

        s_sock.close()
        r_sock.close()

        return arp_rep.src_mac
        
        
if __name__ == '__main__':
    pass