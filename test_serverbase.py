import serverbase
import unittest
import time

class basicTesting(unittest.TestCase):
    servers = [('gopher', 'w8n.koeln.ccc.de', 70),
               ('http', 'w8n.koeln.ccc.de', 80),
               ('ftp', 'w8n.koeln.ccc.de', 21),
               ('gopher', 'w11g.koeln.ccc.de', 70),
               ('http', 'w11g.koeln.ccc.de', 80),
               ('ftp', 'w11g.koeln.ccc.de', 21)] 

    def testDupes(self):
        for x in self.servers:
            serverbase.addServer(x)
            serverbase.addServer(x)

        s = {}
        for i in range(len(self.servers)):
            x = serverbase.getServer()
            self.failIf(s.has_key(x), "duplicates in serverbase")
            s[x] = 1


    def testCompleteness(self):
        for x in self.servers:
            serverbase.addServer(x)

        s = {}
        for i in range(len(self.servers)):
            s[serverbase.getServer()] = 1

        for x in self.servers:
            del s[x]
        

    def testQueueOrder(self):
        for x in self.servers:
            serverbase.addServer(x)
        
        for x in self.servers[:-2]:
            time.sleep(0.1)
            serverbase.updateTried(x)

        serverbase.updateTried(self.servers[-1])

        self.failUnlessEqual(serverbase.getServer(), self.servers[-2])

unittest.main()
