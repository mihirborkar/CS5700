__author__ = 'yummin'

import re
import socket
import string
import sys
import time

class Client():
    def __init__(self,usr,pwd):
        self.host = 'cs5700.ccs.neu.edu'
        self.urls = ['/fakebook/']
        self.visited = []
        self.flag = []
        self.csrftoken = ''
        self.sessionid = ''
        self.socket = socket.create_connection((self.host, 80))
        self.socket.setblocking(0)
        self.usr = usr
        self.pwd = pwd

    def recv_timeout(self, the_socket,timeout=2):
        #total data partwise in an array
        total_data=[];
        data='';

        #beginning time
        begin=time.time()
        while 1:
            #if you got some data, then break after timeout
            if total_data and time.time()-begin > timeout:
                break

            #if you got no data at all, wait a little longer, twice the timeout
            elif time.time()-begin > timeout*2:
                break

            #recv something
            try:
                data = the_socket.recv(8192)
                if data:
                    total_data.append(data)
                    #change the beginning time for measurement
                    begin = time.time()
                else:
                    #sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass

        #join all parts to make final string
        return ''.join(total_data)

    def handleRequest(self, request):
        try :
            #Set the whole string
            self.socket.sendall(request)
        except socket.error:
            #Send failed
            print 'Send failed'
            sys.exit()

        reply = self.recv_timeout(self.socket, 0.25)
        return reply

    def login(self):
        request="GET /accounts/login/?next=/fakebook/ HTTP/1.1\r\nHost: " + self.host + "\r\n\r\n"

        reply = self.handleRequest(request)
        #print ('[DEBUG]Initial Request\'s reply\n' + reply)

        csrf_pattern = re.compile(r'csrftoken=([a-z0-9]+)\;')
        session_pattern = re.compile(r'sessionid=([a-z0-9]+)\;')
        try:
            self.csrftoken = csrf_pattern.findall(reply)[0]
            self.sessionid = session_pattern.findall(reply)[0]
        except IndexError:
            print(reply)
        #print('[DEBUG]csrf:' + self.csrftoken + '\tsession:' + self.sessionid)

        postdata = 'csrfmiddlewaretoken='+ self.csrftoken + '&username=' + self.usr \
                   +'&password=' + self.pwd + '&next=%2Ffakebook%2F'
        request = "POST /accounts/login/ HTTP/1.1\r\nHost: " + self.host + "\r\nContent-Length: "+ str(len(postdata)) +\
                  "\r\nContent-Type: application/x-www-form-urlencoded\r\nCookie: csrftoken=" + self.csrftoken\
                  + "; sessionid=" + self.sessionid + "\r\n\r\n" + postdata
        #print('[DEBUG]Post Request:\n' + request)

        reply = self.handleRequest(request)
        #print ('[DEBUG]POST Request\'s reply\n' + reply)

        try:
            self.sessionid = session_pattern.findall(reply)[0]
        except IndexError:
            print(reply)
        #print('[DEBUG]csrf:' + self.csrftoken + '\tsession:' + self.sessionid)


    def openUrl(self, url):
        request="GET " + url + " HTTP/1.1\r\n" \
                "Host: " + self.host + "\r\n" \
                "Cookie: csrftoken=" + self.csrftoken + "; sessionid=" + self.sessionid + "\r\n\r\n"
        reply = self.handleRequest(request)
        self.visited.append(url)
        return reply

    def findUrl(self, page):
        pattern = re.compile(r'<a href=\"(/fakebook/[a-z0-9//]+)\">')
        links = pattern.findall(page)
        for l in links:
            if l not in self.urls and l not in self.visited:
                self.urls.append(l)

    def findSecretFlag(self, page):
        pattern = re.compile(r'<h2 class=\'secret_flag\' style=\"color:red\">FLAG: (\w+)</h2>')
        flag = pattern.findall(page)
        #print('Page\n' + page)
        if flag:
            self.flag.extend(flag)

    def getStatus(self, page):
        index = string.find(page,' ') + 1
        status = page[index : index + 3]
        if status == 0 or status == 500 or status == 301:
            print('[DEBUG]Abnormal Status Page:\n' + page)
        return status

    def getNewUrl(self, page):
        pass

    def run(self):
        while self.urls and len(self.flag) < 5:
            link = self.urls.pop(0)
            print('[DEBUG]Open link:' + link)
            page = self.openUrl(link)
            status = self.getStatus(page)
            if status == '200':
                self.findUrl(page)
                self.findSecretFlag(page)
            elif status == '403' or status == '404':
                self.visited.append(link)
            elif status == '301':
                self.urls.append(self.getNewUrl(page))
            elif status == '500':
                #self.login()
                self.visited.pop()
                self.urls.insert(0, link)
                #self.urls.insert(0, '/fakebook/')
                print('[DEBUG]Page:\n' + page)

        print('secret_flag:')
        print(self.flag)


def main():
    c = Client('001943970', 'OVM0EEPM')
    c.login()
    c.run()

main()