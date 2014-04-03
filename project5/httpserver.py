from SimpleHTTPServer import SimpleHTTPRequestHandler
import BaseHTTPServer
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

def server(port):
    # Config
    server_address = ('127.0.0.1', port)
    HandlerClass = SimpleHTTPRequestHandler
    ServerClass  = BaseHTTPServer.HTTPServer
    Protocol     = "HTTP/1.0"

    HandlerClass.protocol_version = Protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()

if __name__ == '__main__':
    port, origin = parse(sys.argv)
    server(port)
