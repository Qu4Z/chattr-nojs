#!/usr/bin/env python2

import socket
import sys

host = "localhost"
port = 50007
bufferSize = 1024

tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSocket.connect((host, port))

while True:
	message = raw_input("> ")
	if not message: break
	tcpSocket.sendall(message)
