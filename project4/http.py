import re
import socket
import time
import sys

def recv_timeout(the_socket,timeout=2):
    f = open(filename, 'wb+')
    the_socket.setblocking(0)
    total_data=[];
    data='';
    begin=time.time()
    while 1:
        #if you got some data, then break after wait sec
        if total_data and time.time()-begin>timeout:
            break
        #if you got no data at all, wait a little longer
        elif time.time()-begin>timeout*2:
            break
        try:
            data=the_socket.recv(2048)
            if data:
                f.write(data)
                begin=time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    f.close()

url = sys.argv[1]
if url.endswith('/'):
    filename = 'index.html'
else:
    filename = url.split('/')[-1]

hostname = url.split('/')[2]
start_position = url.find(hostname) + len(hostname)


sock = socket.create_connection((hostname, 80))

request="GET " + url[start_position:] + " HTTP/1.1\r\nHost: " + hostname + "\r\n\r\n"

try :
    sock.sendall(request)
except socket.error:
    #Send failed
    sys.exit('Send failed')

recv_timeout(sock, 0.1)
