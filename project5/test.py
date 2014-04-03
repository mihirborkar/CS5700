import socket

# hostnames = [
# 'ec2-54-84-248-26.compute-1.amazonaws.com',
# 'ec2-54-186-185-27.us-west-2.compute.amazonaws.com',
# 'ec2-54-215-216-108.us-west-1.compute.amazonaws.com',
# 'ec2-54-72-143-213.eu-west-1.compute.amazonaws.com',
# 'ec2-54-255-143-38.ap-southeast-1.compute.amazonaws.com',
# 'ec2-54-199-204-174.ap-northeast-1.compute.amazonaws.com',
# 'ec2-54-206-102-208.ap-southeast-2.compute.amazonaws.com',
# 'ec2-54-207-73-134.sa-east-1.compute.amazonaws.com']
hostnames = ['login.ccs.neu.edu',
'cs5700cdnproject.ccs.neu.edu']

ips = map(socket.gethostbyname, hostnames)

MEASUREMENT_PORT=60532

def select_replica(target):
    dic = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    MESSAGE = target
    for ip in ips:
        sock.sendto(MESSAGE, (ip, MEASUREMENT_PORT))
        latency, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        dic.update({addr[0] : latency})

    sock.close()

    sorted_dic = sorted(dic.items(), key=lambda e:e[1])
    print sorted_dic
    return sorted_dic[0][0]

print select_replica('74.125.236.81')
