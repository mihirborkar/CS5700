import socket

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
    def __init__(self):
        # tcp header fields
        self.tcp_source = 1234   # source port
        self.tcp_dest = 80   # destination port
        self.tcp_seq = 0
        self.tcp_ack_seq = 0
        self.tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
        #tcp flags
        self.tcp_fin = 0
        self.tcp_syn = 1
        self.tcp_rst = 0
        self.tcp_psh = 0
        self.tcp_ack = 0
        self.tcp_urg = 0
        self.tcp_window = socket.htons (5840) #maximum allowed window size
        self.tcp_check = 0
        self.tcp_urg_ptr = 0

        self.tcp_offset_res = (tcp_doff << 4) + 0
        self.tcp_flags = tcp_fin + \
        (tcp_syn << 1) + \
        (tcp_rst << 2) + \
        (tcp_psh << 3) + \
        (tcp_ack << 4) + \
        (tcp_urg << 5)

        # the ! in the pack format string means network order
        tcp_header = pack('!HHLLBBHHH' , \
            tcp_source, \
            tcp_dest, \
            tcp_seq, \
            tcp_ack_seq, \
            tcp_offset_res, \
            tcp_flags,  \
            tcp_window, \
            tcp_check, \
            tcp_urg_ptr)
