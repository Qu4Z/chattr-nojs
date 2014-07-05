#! /usr/bin/env python
# coding: utf-8
#
# WhatsUp Server
#
# Yet another simple socket multi-user chating program
# Please use `telnet IP PORT` to log in
#
# @author:   Xin Wang <sutarshow#gmail.com>
# @version:  1.0
# @since:    16-09-2013
#

import socket
import threading
import time
import logging
import random

HOST = ''
PORT = 8018
TIMEOUT = 1
BUF_SIZE = 1024

WORDS = ["python", "jumble", "easy", "difficult", "answer",  "xylophone"]

class WhatsUpServer(threading.Thread):

    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.ip = self.addr[0]
        self.name = ''

    def print_indicator(self, prompt):
        self.conn.send('%s\n>> ' % (prompt,))

    def login(self):
        global clients
        global messages
        global accounts
        global onlines

        logging.info('Connected from: %s:%s' %
                     (self.addr[0], self.addr[1]))
        clients.add((self.conn, self.addr))
        msg = '\n## Welcome to WhatsUp\n## Enter `!q` to quit\n'
	self.print_indicator(msg)

        # new user
        print accounts
        if self.ip not in accounts:
            accounts[self.ip] = {
                'name': '',
                'lastlogin': time.ctime()
            }
	    name = WORDS.pop()
            accounts[self.ip]['name'] = name
            self.name = name
            logging.info('%s logged as %s' % (self.addr[0], self.name))
            messages[name] = []
            self.print_indicator('## Welcome, enjoy your chat')
        else:
            self.name = accounts[self.ip]['name']
            while 1:
                    self.print_indicator(
                        '## Welcome back, last login: %s' %
                        (accounts[self.ip]['lastlogin'],))
                    accounts[self.ip]['lastlogin'] = time.ctime()
                    break
            self.conn.send(self.show_mentions(self.name))
        self.broadcast('`%s` joined the room' % (self.name,), clients, False)
        onlines[self.name] = self.conn

    def logoff(self):
        global clients
        global onlines
        self.conn.send('## Bye!\n')
        del onlines[self.name]
        clients.remove((self.conn, self.addr))
        if onlines:
            self.broadcast('## `%s` left the room' %
                           (self.name,), clients)
        self.conn.close()
        exit()

    def check_keyword(self, buf):
        global onlines

        if buf.find('!q') == 0:
            self.logoff()

        if buf.find('@') == 0:
            to_user = buf.split(' ')[0][1:]
            from_user = self.name
            msg = buf.split(' ', 1)[1]

            # if user is online
            if to_user in onlines:
                onlines[to_user].send('@%s: %s\n>> ' % (from_user, msg))
                self.mention(from_user, to_user, msg, 1)
            # offline
            else:
                self.mention(from_user, to_user, msg)
            return True

    def mention(self, from_user, to_user, msg, read=0):
        global messages
        # print 'Messages', messages
        if to_user in messages:
            messages[to_user].append([from_user, msg, read])
            self.print_indicator('## Message has sent to %s' % (to_user,))
        else:
            self.print_indicator('## No such user named `%s`' % (to_user,))

    def show_mentions(self, name):
        global messages
        res = '## Here are your messages:\n'
        if not messages[name]:
            res += '   No messages available\n>> '
            return res
        for msg in messages[name]:
            if msg[2] == 0:
                res += '(NEW) %s: %s\n' % (msg[0], msg[1])
                msg[2] = 1
            else:
                res += '      %s: %s\n' % (msg[0], msg[1])
        res += '>> '
        return res

    def broadcast(self, msg, receivers, to_self=True):
        for conn, addr in receivers:
            # if the client is not the current user
            if addr[0] != self.ip:
                conn.send(msg + '\n>> ')
            # if current user
            else:
                self.conn.send('>> ') if to_self else self.conn.send('')

    def run(self):
        global messages
        global accounts
        global clients
        self.login()

        while True:
            try:
		self.conn.settimeout(TIMEOUT)
                buf = self.conn.recv(BUF_SIZE).strip()
		if buf:
	            logging.info('%s@%s: %s' % (self.name, self.addr[0], buf))
                    # check features
                    if not self.check_keyword(buf):
                        # client broadcasts message to all
                        self.broadcast('%s: %s' % (self.name, buf), clients)

            except Exception, e:
                # timed out
                pass

def main():
    global clients
    global messages
    global accounts
    global onlines

    # logging setup
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')

    # initialize global vars
    clients = set()
    messages = {}
    accounts = {}
    onlines = {}

    # set up socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(10)
    print '-= Chat Server =-'
    print '>> Listening on:', PORT
    print '>> Author: Xin Wang'
    print ">> Simplified: Philip Korsika"
    print ''
    
    while True:
	try:
	    conn, addr = sock.accept()
	    server = WhatsUpServer(conn, addr)
	    server.start()
        except Exception, e:
            print e

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Quited'
