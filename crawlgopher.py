#!/usr/local/bin/python -*- Mode: Python; tab-width: 4 -*-

import sys
import socket
import time
import select
import asyncore
import asynchat
import frontier
import urltoolsgopher
import frontier

timeout = 200

class crawl (asynchat.async_chat):
    
    def __init__ (self, address, port, selector):
        '''constuctor - opens connection'''
        asynchat.async_chat.__init__ (self)
        self.create_socket (socket.AF_INET, socket.SOCK_STREAM)
        self.set_terminator ('\r\n')
        self.buffer = ''
        self.host = address
        self.port = port
        self.selector = selector
        self.timestamp = int(time.time())
        self.deadline = self.timestamp + timeout
        self.filelist = []
        try:
            self.connect((address, port))
        except:
            self.handle_error()
            self.close()


    def handle_connect(self):
        '''we have successfull connected'''

        self.push(self.selector + '\r\n')

    def handle_error(self):
        '''print out error information to stderr'''
        
        print >>sys.stderr, self.host, sys.exc_info()[1]

    
    def collect_incoming_data (self, data):
        '''collect data which was recived on the socket'''
        
        self.buffer = self.buffer + data
      
    def found_terminator (self):
        '''we have read a whole line and decide what do do next'''

        self.filelist.append(self.buffer)
        self.buffer = ''


    def handle_close (self):
        '''when the connection is closed use monitor() to start new connections'''
        
        parse(self.filelist, self.host, self.port, self.selector)
        self.close()


def parse(filelist, host, port, selector):

    for line in filelist:
        try:
            # clean lineend
            if line[-2:] == '\r\n':
                line = line[:-2]
            elif line[-1:] in '\r\n':
                line = line[:-1]
            # check if we are/should be finished    
            if line == '.':
                break
            # ignore empty lines
            if not line:
                print '(Empty line from server)'
                continue
        
            gtype = line[0]
            parts = line[1:].split('\t')
            if len(parts) < 4:
                print host, port, repr(selector), ':'
                print '(Bad line from server:', `line`, ')'
                continue
            if parts[2] == 'error.host':
                if not gtype == 'i':
                    print host, port, repr(selector), ':'
                    print '(Server Error:', `line`, ')'
                continue
            if len(parts) > 4:
                if parts[4:] != ['+']:
                    print repr(line)
                    print host, port, repr(selector), ':'
                    print '(Extra info from server:',
                    print parts[4:], ')'
            else:
                parts.append('')
            parts.insert(0, gtype)

            sys.stdout.flush()
            url = urltoolsgopher.genURL(parts[3], parts[4], parts[2])
            if gtype == '1':
                frontier.add(url, host, port)
            else:
                print url
        except:        
            print "error while parsing", host, port, repr(selector), ':', repr(line)
