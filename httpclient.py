#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL] \n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url): 
        host_port = urllib.parse.urlparse(url)
        host = host_port.hostname
        port = host_port.port

        if port is None:
            return (host, 80)
        else:
            return (host, port)
    
    def get_path(self, url):
        path = urllib.parse.urlparse(url).path
        if len(path) == 0:
            return "/"
        else:
            return path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        header = data.split("\r\n")[0]
        code = header.split(" ")[1]
        return int(code)

    def get_headers(self,data):
        headers = data.split("\r\n\r\n")[0]
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        # Parsing URL and creating body
        host, port = self.get_host_port(url)
        path = self.get_path(url)
        body = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"

        # Connecting and formation of response
        self.connect(host, port)
        self.sendall(body)
        self.socket.shutdown(socket.SHUT_WR)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data) 
        print(data)

        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        # Form content for body if it exists
        content = ""
        contentLength = 0
        if args != None:
            for key, value in args.items():  # Seperate keys from value and format them into content
                content += (key + "=" + value + "&")
            content = content[:-1]  # Remove the extra ampersand
            contentLength = len(content)

        # Parsing URL and creating body
        host, port = self.get_host_port(url)
        path = self.get_path(url)
        body = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {contentLength}\r\n\r\n{content}"

        # Connecting and formation of response
        self.connect(host, port)
        self.sendall(body)
        self.socket.shutdown(socket.SHUT_WR)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        print(data) 

        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))