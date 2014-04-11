from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import errno
import getopt
import os
import sys
import urllib2


class CustomizedHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, origin_server, *args):
        self.origin = origin_server
        self.index = {}
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        # TODO: Add map{file:count}
        if not os.path.isfile(os.pardir + self.path):
            # No such file, ask origin server
            self.fetch_origin(self.path)
        else:
            with open(os.pardir + self.path) as f:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f.read())

    def fetch_origin(self, path):
        """Fetch a file from origin server"""
        try:
            res = urllib2.urlopen('http://' + self.origin + ':8080' + path)
        except urllib2.HTTPError:
            # Even origin server does not have such file.
            self.send_error(404, 'File not found: %s' % self.path)
        else:
            filename = os.pardir + path
            d = os.path.dirname(filename)
            if not os.path.exists(d):
                os.makedirs(d)
            f = open(filename, 'w')
            try:
                # TODO: Refactor here
                f.write(res.read())
            except IOError as e:
                if e.errno == errno.EDQUOT:
                    # Disk has no space
                    print 'DISK FULL'
            f.close()


def server(port, origin_server):
    def handler(*args):
        CustomizedHTTPHandler(origin_server, *args)

    httpd = HTTPServer(('', port), handler)
    httpd.serve_forever()

def parse(argvs):
    (port, origin) = (0, '')
    opts, args = getopt.getopt(argvs[1:], 'p:o:')
    for o, a in opts:
        if o == '-p':
            port = int(a)
        elif o == '-o':
            origin = a
        else:
            sys.exit('Usage: %s -p <port> -o <origin>' % argvs[0])
    return (port, origin)


if __name__ == '__main__':
    (port, origin) = parse(sys.argv)
    server(port, origin)
