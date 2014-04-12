from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import errno
import getopt
import os
import sys
import urllib2


class CustomizedHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, origin, cache, *args):
        self.origin = origin
        self.cache = cache
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        print '[DEBUG]Cache:', self.cache
        if self.path not in self.cache:
            # No such file, fetch this file from origin server
            print '[DEBUG]Ask origin server for %s' % self.path
            self.fetch_origin(self.path)
        # File is in server
        with open(os.pardir + self.path) as f:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f.read())
        # Update cache
        self.cache.remove(self.path)
        self.cache.append(self.path)
        print '[DEBUG]Cache:', self.cache

    def fetch_origin(self, path):
        """Fetch a file from origin server
        Args:
            path: the relative path of the file
        """
        try:
            res = urllib2.urlopen('http://' + self.origin + ':8080' + path)
        except urllib2.HTTPError as he:
            self.send_error(he.code, he.reason)
        except urllib2.URLError as ue:
            self.send_error(ue.reason)
        else:
            print '[DEBUG]Try to download %s' % path
            self.download(path, res)

    def download(self, path, response):
        """Download the file from the origin server.
        Args:
            path:
            response:
        """
        filename = os.pardir + path
        d = os.path.dirname(filename)
        is_downloaded = False
        if not os.path.exists(d):
            os.makedirs(d)
        f = open(filename, 'w')
        while not is_downloaded:
            try:
                f.write(response.read())  # Download succeed
                is_downloaded = True
                self.cache.append(path)
            except IOError as e:
                if e.errno == errno.EDQUOT:  # Disk has no space
                    print '[DEBUG]DISK IS FULL'
                    # Update cache
                    # Remove stack bottom element
                    remove_file_path = self.cache.pop(0)
                    # Delete this file
                    os.remove(os.pardir + remove_file_path)
                    print '[DEBUG]Delete %s' % remove_file_path
        f.close()


def server(port, origin):
    cache = []

    def handler(*args):
        CustomizedHTTPHandler(origin, cache, *args)

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
    return port, origin


if __name__ == '__main__':
    port_number, origin_server = parse(sys.argv)
    server(port_number, origin_server)
