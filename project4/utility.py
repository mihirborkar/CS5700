import commands
import fcntl
import socket
import struct


class Packet:

    def __init__(self):
        pass

    def build(self):
        pass

    def rebuild(self, raw_packet):
        pass

    def debug_print(self):
        pass


class RawSocket:

    def __init__(self):
        pass

    def send(self, data):
        pass

    def recv(self):
        pass


def get_open_port():
    """Get a free port for TCP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def get_mac_address(iface='eth0'):
    """Return the MAC address of the localhost"""
    mac = commands.getoutput("ifconfig " + iface + " | grep HWaddr | awk '{ print $5 }'")
    if len(mac) == 17:
        return mac.replace(':', '')


def get_localhost_ip(iface='eth0'):
    """Return the IP address of localhost"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                            0x8915,  # SIOCGIFADDR
                            struct.pack('256s', iface[:15]))[20:24])


def get_gateway_ip():
    """Return the IP address of the default gateway."""
    gateway_ip = ''
    data = commands.getoutput('route -n').split('\n')
    for line in data:
        record = line.split()
        if record[0] == '0.0.0.0':
            gateway_ip = record[1]
            break
    return gateway_ip


def checksum(data):
    """Compute the checksum"""
    pos = len(data)
    if pos & 1:  # If odd...
        pos -= 1
        s = ord(data[pos])  # Prime the sum with the odd end byte
    else:
        s = 0

    # Main code: loop to calculate the checksum
    while pos > 0:
        pos -= 2
        s += (ord(data[pos + 1]) << 8) + ord(data[pos])

    s = (s >> 16) + (s & 0xffff)
    s += (s >> 16)

    result = (~ s) & 0xffff  # Keep lower 16 bits
    result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes
    return result

if __name__ == "__main__":
    print 'MAC Address: ' + get_mac_address()
    print 'IP Address: ' + get_localhost_ip()
    print 'Default Gateway IP Address: ' + get_gateway_ip()
