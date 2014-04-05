from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from os import pardir, sep
import getopt
import sys


def parse(argvs):
    port = 0
    origin = ''

    opts, args = getopt.getopt(argvs[1:],'p:o:')

    for o, a in opts:
        if o == '-p':
            port = int(a)
        elif o == '-o':
            origin = a
        else:
            print 'Usage: %s -p <port> -o <origin>' % argvs[0]

    return port, origin

class CustomizedHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            f = open(pardir + sep + self.path)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        except IOError:
            # No such file, ask origin server
            self.send_error(404, 'File Not Found: %s' % self.path)

def server(port):
    httpd = HTTPServer(('', port), CustomizedHTTPHandler)
    # sa = httpd.socket.getsockname()
    # print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()

if __name__ == '__main__':
    port, origin = parse(sys.argv)
    server(port)
