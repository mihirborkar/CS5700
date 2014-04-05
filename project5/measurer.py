import commands
import socket
import SocketServer
import time

MEASUREMENT_PORT = 60532

class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        target_ip = self.request[0].strip()
        print '[DEBUG]Measure latency to:', target_ip
        sock = self.request[1]
        # avg_time = self.get_avg_time(target_ip)
        avg_time = self.get_connection_time(target_ip)
        sock.sendto(avg_time, self.client_address)

    def get_avg_time(self, ip_address):
        """
        extract average time from ping -c
        """
        cmd = "ping -c 1 " + ip_address + " | tail -1| awk '{print $4}' | cut -d '/' -f 2"
        res = commands.getoutput(cmd)
        return res

    def get_connection_time(self, ip_address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        start = time.time()
        try:
            sock.connect((ip_address, 22))
        except socket.error:
            res = 'inf'
        else:
            end = time.time()
            res = str((end - start) * 1000)
        finally:
            sock.close()
        return res

class MeasurementServer:
    def __init__(self, port=MEASUREMENT_PORT):
        self.port = port

    def start(self):
        server = SocketServer.UDPServer(('', self.port), UDPHandler)
        server.serve_forever()

if __name__ == '__main__':
    server = MeasurementServer()
    server.start()
