# $Id: test_urlbase.py,v 1.1 2002/01/28 22:26:22 drt Exp $

"""unittests for urlbase

  --drt@un.bewaff.net
"""

import unittest
import urlbase
import time

class basicTesting(unittest.TestCase):

    urls = [('server1', 'url1-1'), ('server2', 'url2-1'),
            ('server2', 'url2-2'), ('server3', 'url3-1'),
            ('server3', 'url3-2'), ('server3', 'url3-3'),
            ('server4', 'url4-1'), ('server4', 'url4-2'),
            ('server4', 'url4-3'), ('server4', 'url4-4')]

    def testCompleteness(self):
        for (server, url) in self.urls:
            urlbase.addURL(server, url)

        s = {}
        for (server, url) in self.urls:
            x = urlbase.getURL(server)
            s[(server, x)] = 1

        for x in self.urls:
            del s[x]

    def testServerRemoval(self):
        servers = {}
        for (server, url) in self.urls:
            urlbase.addURL(server, url)
            if not servers.has_key(server):
                servers[server] = 0
            servers[server] += 1

        for x in servers.keys():
            for i in range(servers[x]):
                self.assertNotEqual(urlbase.getURL(x), None, "Removal from server queue is broken - qoeue empty")
            self.assertEqual(urlbase.getURL(x), None, "Removal from server queue is broken - queue nit empty")
            

unittest.main()
