import commands
import fcntl
import socket
import struct


def get_mac_address(iface):
    # mac = commands.getoutput("ifconfig " + iface + "| grep ether | awk '{ print $2 }'")
    # for Linux
    mac = commands.getoutput("ifconfig " + iface + " | grep HWaddr | awk '{ print $5 }'")

    if len(mac) == 17:
        return mac


def get_localhost_ip(ifname='eth0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def checksum(msg):
    s = 0
    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
        s += w
    s = (s >> 16) + (s & 0xffff)
    s += (s >> 16)
    #complement and mask to 4 byte short
    s = ~s & 0xffff
    return s

if __name__ == "__main__":
    print 'MAC Address: ' + get_mac_address('eth0')
    print 'IP Address: ' + get_localhost_ip()
    print get_ip_address('eth0')
