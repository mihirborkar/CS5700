import socket
import time
import sys


class HTTPPacket():
    def __init__(self, url):
        def get_hostname(url):
            # e.g. url: http://cs5700.ccs.neu.edu/fakebook
            # hostname: cs5700.ccs.neu.edu
            hostname = url.split('/')[2]
            #print '[DEBUG]: Host name' + hostname
            return hostname

        def get_relative_path(url, hostname):
            start_position = url.find(hostname) + len(hostname)
            #print '[DEBUG] Path:' + url[start_position:]
            return url[start_position:]

        self.hostname = get_hostname(url)
        self.path = get_relative_path(url, self.hostname)

    def build_request(self):
        request="GET " + self.path + \
         " HTTP/1.1\r\n" + \
         "Host: " + self.hostname + \
         "\r\n\r\n"

        #print '[DEBUG]: HTTP Request\n' + request
        return request


class HTTPSocket:
    def __init__(self, url):
        def get_filename(url):
            # e.g. url: http://cs5700.ccs.neu.edu/fakebook
            # filename: index.html
            if url.endswith('/'):
                filename = 'index.html'
            else:
                filename = url.split('/')[-1]
            #print '[DEBUG]: File name' + filename
            return filename

        self.packet = HTTPPacket(url)
        self.filename = get_filename(url)
        self.sock = socket.create_connection((self.packet.hostname, 80))

    def send(self):
        try:
            request = self.packet.build_request()
            self.sock.sendall(request)
        except socket.error:
            #Send failed
            sys.exit('Send failed')

    def recv(self, timeout=2.0):
        """
        Receive data and write it to a file
        """
        f = open(self.filename, 'wb+')
        self.sock.setblocking(0)
        total_data = []
        data = ''
        begin=time.time()
        while True:
            #if you got some data, then break after wait sec
            if total_data and time.time()-begin > timeout:
                break
            #if you got no data at all, wait a little longer
            elif time.time() - begin > timeout * 2:
                break
            try:
                data = self.sock.recv(2048)
                if data:
                    if data.startswith('HTTP/1.1'):
                        pos = data.find('\r\n\r\n') + 4
                        f.write(data[pos:])
                    else:
                        f.write(data)
                    begin = time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        f.close()

    def get_status(self):
        # TODO get HTTP status code of response packet
        pass

    def close(self):
        self.sock.close()


if __name__ == "__main__":
    url = sys.argv[1]
    sock = HTTPSocket(url)
    sock.send()
    sock.recv(0.1)
    sock.close()
