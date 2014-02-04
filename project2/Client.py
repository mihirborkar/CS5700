__author__ = 'yummin'
__author__ = 'zsyqq'
'''
This is the code for NEU CS5700 project2.
'''

import re
import socket
import string
import sys

class ClientError(Exception):
    def __str__(self):
        return repr(self.value)

class ServerError(Exception):
    def __str__(self):
        return repr(self.value)

class RedirectError(Exception):
    def __str__(self):
        return repr(self.value)

class UnKnowError(Exception):
    def __str__(self):
        return repr(self.value)

class Client():
    '''
    The Client class.
    '''
    def __init__(self,usr,pwd):
        '''
        Initial the class
        '''
        self.host = 'cs5700.ccs.neu.edu'#host name
        self.urls = ['/fakebook/']#store unvisited urls
        self.visited = []#store visited urls
        self.flag = []#store secret flags
        self.csrftoken = ''#cookie's csrftoken
        self.sessionid = ''#cookie's sessionid
        self.usr = usr#user name
        self.pwd = pwd#password
        #Connect to remote server
        self.sock = socket.create_connection((self.host, 80))

    def handleRequest(self, request):
        '''
        Send request to the server and receive response. Return the response
        '''
        try :
            self.sock.sendall(request)
        except socket.error:
            #Send failed
            sys.exit('Send failed')

        reply = self.sock.recv(4096)
        return reply

    def login(self):
        '''
        Login to the fakebook and get cookie.
        '''
        #initial request to access fakebook
        request="GET /accounts/login/?next=/fakebook/ HTTP/1.1\r\nHost: " + self.host + "\r\n\r\n"

        reply = self.handleRequest(request)
        #print ('[DEBUG]Initial Request\'s reply\n' + reply)

        #Use regular expression to get the cookie's value
        csrf_pattern = re.compile(r'csrftoken=([a-z0-9]+)\;')
        session_pattern = re.compile(r'sessionid=([a-z0-9]+)\;')
        #get cookie
        try:
            self.csrftoken = csrf_pattern.findall(reply)[0]
            self.sessionid = session_pattern.findall(reply)[0]
        except IndexError:
            #server's reponse is abnormal, cannot get the cookie value
            #print('[DEBUG]Cannot parse1:\n' + reply)
            sys.exit('Cannot parse HTML due to receive incomplete message.')
        #print('[DEBUG]csrf:' + self.csrftoken + '\tsession:' + self.sessionid)

        #Post request to server, send username and password to login fakebook
        postdata = 'csrfmiddlewaretoken='+ self.csrftoken + '&username=' + self.usr \
                   +'&password=' + self.pwd + '&next='
        request = "POST /accounts/login/ HTTP/1.1\r\nHost: " + self.host + "\r\nConnection: keep-alive\r\nContent-Length: "\
        + str(len(postdata)) +"\r\nContent-Type: application/x-www-form-urlencoded\r\nCookie: csrftoken="\
        + self.csrftoken + "; sessionid=" + self.sessionid + "\r\n\r\n" + postdata
        #print('[DEBUG]Post Request:\n' + request)

        reply = self.handleRequest(request)
        #print ('[DEBUG]POST Request\'s reply\n' + reply)
        try:
            self.sessionid = session_pattern.findall(reply)[0]
        except IndexError:
            #print('[DEBUG]Cannot parse2:\n' + reply)
            sys.exit('Cannot parse HTML due to receive incomplete message.')
        #print('[DEBUG]csrf:' + self.csrftoken + '\tsession:' + self.sessionid)


    def openUrl(self, url):
        '''
        Open the given url and return the reponse from the server
        '''
        def getStatus(page):
            '''
            Parse the HTTP response header and get HTTP status code
            '''
            index = string.find(page,' ') + 1
            status = page[index : index + 3]
            # if status == '' or status == '500' or status == '301':
            #     print('[DEBUG]Abnormal Status Page:' + status + '\n' + page)
            return status

        request="GET " + url + " HTTP/1.1\r\n" \
                "Host: " + self.host + "\r\nConnection: keep-alive\r\n" \
                "Cookie: csrftoken=" + self.csrftoken + "; sessionid=" + self.sessionid + "\r\n\r\n"
        page = self.handleRequest(request)
        self.visited.append(url)#this url is visited
        status = getStatus(page)
        if status == '403' or status == '404':
            raise ClientError('403 or 404 Error')
        elif status == '301':#redirect to a new url
             raise RedirectError('301 Error')
        elif status == '500':#Internal Server Error
            raise ServerError('500 Error')
        elif status =='':
            raise UnKnowError('Unkonwn Error')
        return page

    def findUrl(self, page):
        '''
        Use regular expression to find urls in html page
        '''
        pattern = re.compile(r'<a href=\"(/fakebook/[a-z0-9/]+)\">')
        links = pattern.findall(page)
        #Find a new url(have not been visited or found), then add it to urls
        self.urls.extend(filter(lambda l: l not in self.urls and l not in self.visited, links))

    def findSecretFlag(self, page):
        '''
        Use regular expression to find secret flag in html page
        '''
        pattern = re.compile(r'<h2 class=\'secret_flag\' style=\"color:red\">FLAG: (\w+)</h2>')
        flag = pattern.findall(page)
        #print('Page\n' + page)
        if flag:
            self.flag.extend(flag)

    def getNewUrl(self, page):
        '''
        Parse the HTTP response header and get new url
        '''
        pattern = re.compile(r'Location=http://cs5700\.ccs\.neu\.edu(/fakebook/[a-z0-9/]+)')
        new_url = pattern.findall(page)[0]
        return new_url

    def run(self):
        '''
        Use bridth first search to crawl fakebook
        '''
        while self.urls and len(self.flag) < 5:#if there are unvisited urls or less than 5 flags, countinue the loop
            link = self.urls.pop(0)
            #print('[DEBUG]Open link:' + link)
            try:
                page = self.openUrl(link)
                #print('[DEBUG]Page:\n' + page)
                self.findUrl(page)
                self.findSecretFlag(page)
            except ClientError:
                self.visited.append(link)#abandon the URL
            except RedirectError:
                self.urls.insert(0, self.getNewUrl(page))
            except ServerError:
                self.sock = socket.create_connection((self.host, 80))
                self.visited.pop()
                self.urls.insert(0, link)
            except UnKnowError:
                self.sock = socket.create_connection((self.host, 80))
                self.visited.pop()
                self.urls.insert(0, link)

        # print('[DEBUG]Visited:' + str(len(self.visited)))
        # print(self.visited)
        # print('[DEBUG]URLS:' + str(len(self.urls)))
        # print(self.urls)
        # print('[DEBUG]secret_flag:')
        for flag in self.flag:
            print flag
        self.sock.close()

def main():
    #c = Client('001943970', 'OVM0EEPM')
    #c = Client('001944902', 'AF50YTLA')
    if(len(sys.argv) != 3):
        sys.exit('Illeagal Arguments.')
    c = Client(sys.argv[1], sys.argv[2])
    c.login()
    c.run()

if __name__ == '__main__':
    main()
