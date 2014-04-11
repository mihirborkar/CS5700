import socket
import threading

hostnames = ['ec2-54-84-248-26.compute-1.amazonaws.com',
             'ec2-54-186-185-27.us-west-2.compute.amazonaws.com',
             'ec2-54-215-216-108.us-west-1.compute.amazonaws.com',
             'ec2-54-72-143-213.eu-west-1.compute.amazonaws.com',
             'ec2-54-255-143-38.ap-southeast-1.compute.amazonaws.com',
             'ec2-54-199-204-174.ap-northeast-1.compute.amazonaws.com',
             'ec2-54-206-102-208.ap-southeast-2.compute.amazonaws.com',
             'ec2-54-207-73-134.sa-east-1.compute.amazonaws.com']
# hostnames = ['login.ccs.neu.edu', 'cs5700cdnproject.ccs.neu.edu']

MEASUREMENT_PORT = 60532
dic = {}


class testThread(threading.Thread):
    def __init__(self, host, target, execute_lock):
        threading.Thread.__init__(self)
        self.host = host
        self.target = target
        self.lock = execute_lock

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = socket.gethostbyname(self.host)
        try:
            sock.connect((ip, MEASUREMENT_PORT))
            sock.sendall(self.target)
            latency = sock.recv(1024)
        except socket.error as e:
            print '[Error]Connect Measurer' + str(e)
            latency = 'inf'
        finally:
            sock.close()

        print '[DEBUG]IP: %s\tLatency:%s' % (ip, latency)
        self.lock.acquire()
        dic.update({ip: float(latency)})
        self.lock.release()


def select_replica(target_ip):
    lock = threading.Lock()
    threads = []

    for i in range(len(hostnames)):
        t = testThread(hostnames[i], target_ip, lock)
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    sorted_dic = sorted(dic.items(), key=lambda e: e[1])
    print sorted_dic
    return sorted_dic[0][0]


if __name__ == '__main__':
    print '[DEBUG]Select replica server:'
    print select_replica('139.82.16.196')
