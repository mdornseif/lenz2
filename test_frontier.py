import unittest
import frontier

class basicTesting(unittest.TestCase):

    urlsin = ["gopher://w8n.koeln.ccc.de:8070/","http://w8n.koeln.ccc.de/",
              "gopher://w8n.koeln.ccc.de/", "http://w8n.koeln.ccc.de:8080/",
              "gopher://w11g.koeln.ccc.de/", "http://w11g.koeln.ccc.de/"]
    urlsout = ["gopher://w8n.koeln.ccc.de:8070/","http://w8n.koeln.ccc.de:80/",
              "gopher://w8n.koeln.ccc.de:70/", "http://w8n.koeln.ccc.de:8080/",
              "gopher://w11g.koeln.ccc.de:70/", "http://w11g.koeln.ccc.de:80/"]
    
    def testInOut(self):
        for x in self.urlsin:
            frontier.add(x)

        print frontier.serverbase.serverlist

        u = {}
        x = frontier.getURL()
        while x != None:
            u[x] = 1
            print x
            x = frontier.getURL()

        for x in self.urlsout:
            del u[x]

        self.failUnless(len(u) == 0)

unittest.main()
