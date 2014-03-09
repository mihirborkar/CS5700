import socket
import sys
from struct import pack, unpack
from utility import get_mac_address

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
        
    def create(self):
        pass
    
    def recreate(self):
        pass
        
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
        
    def create(self, src_mac, src_ip, dst_mac, dst_ip):
        self.op = ARPOP_REQUEST
        self.src_mac = ''
        self.src_ip = ''
        self.dst_mac = ''
        self.dst_ip = ''
        arpfram = pack('!HHBBH6s4s6s4s',
                       self.htype,
                       self.ptype,
                       self.hlen,
                       self.plen,
                       self.op,
                       self.src_mac,
                       self.src_ip,
                       self.dst_mac,
                       self.dst_ip)
        

class Ethernet_Socket:
    def __init__(self):
        self.send_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
        self.send_sock.bind(('eth0', socket.SOCK_RAW))
        
        self.recv_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
        self.recv_sock.setblocking(0)

        self.src_mac = ''
        
    def send(self):
        packet = Ethernet_Packet()
        
    def recv(self):
        pass
        
    def find(self, dst_ip):
        s_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
        r_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
        r_sock.settimeout(1)
        
        self.src_mac = get_mac_address('eth0')
        arp_pack = ARP_Packet()
        
        
if __name__ == '__main__':
    pass