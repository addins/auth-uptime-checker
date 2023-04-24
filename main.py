import logging
import requests

def check_stp_auth(baseUrlNoPrefix, useHttps, authUri, username, password):
    prefix = 'https://' if useHttps else 'http://' 
    baseUrl = prefix + baseUrlNoPrefix
    authUrl = baseUrl + authUri
    authRequestBody = {'username': username, 'password': password}
    
    session = requests.Session()
    resp1 = session.get(baseUrl)
    csrfToken = session.cookies['XSRF-TOKEN']
    headers = {
        'X-XSRF-TOKEN': csrfToken,
        'Cookie': 'XSRF-TOKEN=' + csrfToken,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    req = requests.Request(method='POST', url=authUrl, json=authRequestBody, headers=headers)
    preppedReq = req.prepare()
    return session.send(preppedReq)

from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
import os
import time
from socketserver import ThreadingMixIn
import threading

class Server(BaseHTTPRequestHandler):
    baseUrl = 'service-uri-without-http-prefix:443'
    useHttps = True
    authUri = '/auth/login'
    username = 'user'
    password = 'pass'

    def do_GET(self):
        load_dotenv(verbose=True)
        self.baseUrl = os.getenv('BASE_URL', self.baseUrl)
        self.useHttps = os.getenv('USE_HTTPS', self.useHttps)
        self.authUri = os.getenv('AUTH_URI', self.authUri)
        self.username = os.getenv('USERNAME', self.username)
        self.password = os.getenv('PASSWORD', self.password)
        
        httpResp = check_stp_auth(self.baseUrl, self.useHttps, self.authUri, self.username, self.password)
        self.send_response(httpResp.status_code)
        self.send_header("Content-Type", httpResp.headers['Content-Type'])
        self.end_headers()
        self.wfile.write(httpResp.content if httpResp.status_code != 200 else bytes('OK', 'utf-8'))
        
    @staticmethod
    def startServer(hostname, port):
        webServer = HTTPServer((hostname, port), Server)
        print('Server started http://%s:%s' % (hostname, port))
        threading.Thread(target=webServer.serve_forever).start()
        
    
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    @staticmethod
    def startServer(hostname, port):
        webServer = ThreadedHTTPServer((hostname, port), Server)
        print('Server started http://%s:%s' % (hostname, port))
        threading.Thread(target=webServer.serve_forever).start()
        

if __name__ == '__main__':
    hostname = "0.0.0.0"
    port = 8080
    ThreadedHTTPServer.startServer(hostname, port)