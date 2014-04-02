import socket
import time

# hosts = ['ec2-54-85-28-148.compute-1.amazonaws.com',
# 'ec2-54-84-248-26.compute-1.amazonaws.com',
# 'ec2-54-186-185-27.us-west-2.compute.amazonaws.com',
# 'ec2-54-215-216-108.us-west-1.compute.amazonaws.com',
# 'ec2-54-72-143-213.eu-west-1.compute.amazonaws.com',
# 'ec2-54-255-143-38.ap-southeast-1.compute.amazonaws.com',
# 'ec2-54-199-204-174.ap-northeast-1.compute.amazonaws.com',
# 'ec2-54-206-102-208.ap-southeast-2.compute.amazonaws.com',
# 'ec2-54-207-73-134.sa-east-1.compute.amazonaws.com']

hosts = ['www.google.com',
'www.google.com.hk',
'www.google.co.uk',
'www.google.co.jp']

def measure(host, port=80):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	start = time.time()
	s.connect((socket.gethostbyname(host), port))
	end = time.time()
	s.close()
	return end - start

if __name__ == '__main__':
	times = []
	for host in hosts:
		times.append(measure(host))

	dic = dict(zip(hosts, times))
	sorted_dic = sorted(dic.items(), key=lambda e:e[1])
	print sorted_dic
	index = [item[0] for item in sorted_dic]
	print index
