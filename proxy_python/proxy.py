import socket, _thread, select
from gephiAPI import *

__version__ = '0.1.0 Draft 1'
BUFLEN = 8192
VERSION = 'Python Proxy/'+__version__
HTTPVER = 'HTTP/1.1'

class ConnectionHandler:
    def __init__(self, connection, address, timeout):
        self.client = connection
        self.client_buffer = ''
        self.timeout = timeout
        self.method, self.path, self.protocol = self.get_base_header()
        if self.method=='CONNECT':
            #self.method_CONNECT()
            self.method_others()
        elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT',
                             'DELETE', 'TRACE'):
            self.method_others()
        self.client.close()
        self.target.close()

    def get_base_header(self):
        while 1:
            self.client_buffer += self.client.recv(BUFLEN).decode()
            end = self.client_buffer.find('\n')
            referer = self.client_buffer.find('Referer:')
            host = self.client_buffer.find('Host:')
            if end!=-1:
                break
        #print '%s'%self.client_buffer[:end]#debug
        data = (self.client_buffer[:end+1]).split()
        #print '%s'%self.client_buffer # data#debug
        referer = (self.client_buffer[referer:]).split()
        host = (self.client_buffer[host:]).split()
        print('url: ',data[1])
        print('host: ',host[1])
        gephi.add_node(host[1])
        gephi.add_node(data[1])
        if len(referer) >= 1:
           print('ref: ',referer[1])
           gephi.add_node(referer[1])
           gephi.add_edge(source=data[1], target=referer[1])
        else:
           print('no ref')
        gephi.add_edge(source=data[1], target=host[1])
        #print 'data :',data
        self.client_buffer = self.client_buffer[end+1:]
        return data

    def method_CONNECT(self):
        self._connect_target(self.path)
        #self.client.send(HTTPVER+' 200 Connection established\n'+
        #                 'Proxy-agent: %s\n\n'%VERSION)
        self.client_buffer = ''
        self._read_write()        

    def method_others(self):
        #self.path = self.path[7:]
        i = self.path.find('/')
        host = self.path[:i]        
        path = self.path[i:]
        self._connect_target(host)
        self.target.send(('%s %s %s\n'%(self.method, self.path, self.protocol)+
                         self.client_buffer).encode())
        self.client_buffer = ''
        self._read_write()

    def _connect_target(self, host):
        #i = host.find(':')
        #if i!=-1:
        #    port = int(host[i+1:])
        #    host = host[:i]
        #else:
        #    port = 80
        host='proxyweb.utc.fr'
        port=3128
        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(soc_family)
        self.target.connect(address)

    def _read_write(self):
        time_out_max = self.timeout/3
        socs = [self.client, self.target]
        count = 0
        while 1:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN).decode()
                    #print 'some data:', '%s'%data
                    if in_ is self.client:
                        out = self.target
                    else:
                        out = self.client
                    if data:
                        out.send((data.econde()))
                        count = 0
            if count == time_out_max:
                break

def start_server(host='localhost', port=8080, IPv6=False, timeout=60,
                  handler=ConnectionHandler):
    if IPv6==True:
        soc_type=socket.AF_INET6
    else:
        soc_type=socket.AF_INET
    soc = socket.socket(soc_type)
    soc.bind((host, port))
    print("Serving on %s:%d."%(host, port))#debug
    soc.listen(0)
    while 1:
        try:
           _thread.start_new_thread(handler, soc.accept()+(timeout,))
        except KeyboardInterrupt:
           soc.close()
           exit()

gephi = GephiAPI("localhost",8081)

if __name__ == '__main__':
    start_server()
