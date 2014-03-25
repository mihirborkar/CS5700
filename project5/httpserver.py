import sys, getopt

port=0
origin=''

opts, args = getopt.getopt(sys.argv[1:],'p:o:')

for o, a in opts:
    if o == '-p':
        port = a
    elif o == '-o':
        origin = a
    else:
        print 'Usage: %s -p <port> -o <origin>' % sys.argv[0]

print port
print origin
