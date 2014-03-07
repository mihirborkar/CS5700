import socket
import struct
import sys

class Ethernet_Packet:

    def __init__(self, data):
        self.data = data
        self.sock = socket.socket()
