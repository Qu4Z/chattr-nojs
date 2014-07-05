#!/usr/bin/env python2

import socket
from threading import Thread
import sys

host = ""
port = 50007
bufferSize = 1024

tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSocket.bind((host,port))
tcpSocket.listen(10)

conn, addr = tcpSocket.accept()
print "Connected by", addr

while True:
	data = conn.recv(bufferSize)
	if not data: sys.exit(0)
	print data

conn.close()
