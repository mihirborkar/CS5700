import socket
import commands

def get_MAC_address(iface):
    mac = commands.getoutput("ifconfig " + iface + "| grep ether | awk '{ print $2 }'")
    # for Linux
    # mac = commands.getoutput("ifconfig " + iface + " | grep HWaddr | awk '{ print $5 }'")
    if len(mac)==17:
        return mac

def get_IP_address():
    return socket.gethostbyname(socket.gethostname())

# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0

    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        s = s + w

    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);

    #complement and mask to 4 byte short
    s = ~s & 0xffff

    return s

if __name__ == "__main__":
    print 'MAC Address: ' + get_MAC_address('en0')
    print 'IP Address: ' + get_IP_address()
