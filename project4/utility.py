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

if __name__ == "__main__":
    print 'MAC Address: ' + get_MAC_address('en0')
    print 'IP Address: ' + get_IP_address()
