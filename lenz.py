#!/usr/bin/python

'''A very simple gopherspace spider by drt.

It writes all typte, host, port, selector information it finds to stdout.

by drt - http://koeln.ccc.de/drt/
'''

import Queue
import gopherlib
import time
import sys
import traceback

# mimimum seconds pause between fetching two files from the same server
hostpause = 30

faildhosts = {}
visitedhosts = {} 

def spider(todo):

    retry = Queue.Queue()
    hosttimings = {}
    
    while not todo.empty():
        while not todo.empty():
            (selector, host, port) = todo.get()
            now = time.time()
            if hosttimings.has_key(host) and (hosttimings[host] + hostpause > now):
                retry.put((selector, host, port))
                continue
            hosttimings[host] = time.time()
            try:
                print >>sys.stderr, host, port, repr(selector),
                sys.stderr.flush()
                filelist = gopherlib.get_directory(gopherlib.send_selector(selector, host, port))
                print >>sys.stderr, len(filelist)
                sys.stderr.flush()
                
                key = host + ':' + str(port)
                if not visitedhosts.has_key(key):
                    visitedhosts[key] = [selector]
                else:
                    visitedhosts[key].append(selector)
                    
                for x in filelist:
                    (type, name, selector, host, port, foo) = x
                    if type != 'i' and type != '3' and host != 'error.host':
                        print '%s\t%s\t%s' % (selector, host, port)
                    if type == '1':
                        key = host + ':' + str(port)
                        if not (visitedhosts.has_key(key) and selector in visitedhosts[key]):
                            todo.put((selector, host, port))
            except:
                print >>sys.stderr, 'failed'                                    
                # traceback.print_exc(file=sys.stdout)

                                    
        print >>sys.stderr, "pausing to give servers a rest, queuesize:", retry.qsize()
        time.sleep(hostpause / 2)
        todo = retry
        retry = Queue.Queue()


def main():
    todo = Queue.Queue()
    todo.put(('1/', 'w8n.koeln.ccc.de', 70))
    todo.put(('1/', 'gopher.floodgap.com', 70))
    todo.put(('1/', 'gopher.nct.de', 70))
    spider(todo)

main()
