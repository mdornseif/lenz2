import time

class server:

    def __init__(self, proto, host, port):
        self.proto = proto
        self.host = host
        self.port = port
        self.lastretrival = 0
        self.lasttry = 0
        self.ip = None

    def triedNow(self):
        self.lasttry = time.time()

    def retrivedNow(self):
        self.triedNow()
        selt.lastretrival = self.lasttry

    def getID(self):
        return ((self.proto, self.host, self.port))

    def getIP(self):
        if self.ip == None:
            self.ip = socket.gethostbyname(self.host)
        return self.ip

    def getInfo(self):
        return (self.proto, self.host, self.port)
    

serverlist = {}

def addServer(key):
    (proto, host, port) = key
    if not serverlist.has_key(key):
        serverlist[key] = server(proto, host, port)

def updateRetrived(key):
    # addServer(serverlist[key].getInfo())
    serverlist[key].retrivedNow()
    
def updateTried(key):
    # addServer(serverlist[key].getInfo())
    serverlist[key].triedNow()

def getServer():

    if len(serverlist) == 0:
        return None
    
    # find lowest lasttry
    lowesttry = time.time()
    for k in serverlist.keys():
        x = serverlist[k]
        if x.lasttry < lowesttry:
            lowesttry = x.lasttry
            lowestentry = x.getID()

    updateTried(lowestentry)
    return lowestentry
