import commands
import SocketServer

MEASUREMENT_PORT=60532

class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        target_ip = self.request[0].strip()
        print '[DEBUG]', target_ip
        sock = self.request[1]
        avg_time = self.get_avg_time(target_ip)
        sock.sendto(avg_time, self.client_address)

    def get_avg_time(self, ip_address):
        """
        extract average time from ping -c
        """
        cmd = "ping -c 1 " + ip_address + " | tail -1| awk '{print $4}' | cut -d '/' -f 2"
        res = commands.getoutput(cmd)
        return res

class MeasurementServer:
    def __init__(self, port=MEASUREMENT_PORT):
        self.port = port

    def start(self):
        HOST, PORT = '', self.port
        server = SocketServer.UDPServer((HOST, PORT), UDPHandler)
        server.serve_forever()

if __name__ == '__main__':
    server = MeasurementServer()
    server.start()
