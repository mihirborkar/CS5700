import sys, getopt

port=0
name=''

opts, args = getopt.getopt(sys.argv[1:],'p:n:')

for o, a in opts:
	if o == '-p':
		port = a
	elif o == '-n':
		name = a
	else:
		print 'Usage: %s -p <port> -n <name>' % sys.argv[0]

print port
print name
