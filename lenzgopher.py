import frontier
import monitor
import gopher        
import urltoolsgopher

class gopherRequestor(gopher.gopherClient):
    def __init__(self, selector = '', binary = 0):
        gopher.gopherClient.__init__(self, selector, binary)
        monitor.addConnection()

    def connectionMade(self):
        self.sendSelector(self.selector + '\r\n')

    def connectionLost(self):
        gopher.gopherClient.connectionLost(self)
        monitor.delConnection()
    
    def handleResponse(self, buffer):
        parseGopherReply(buffer)

def parseGopherReply(data):
    for x in data:
        try:
            x = x.strip()
            if len(x) == 0:
                break
            # check if we are/should be finished    
            if x == '.':
                break
            t = x[0]
            fields = x[1:].split('\t')
            if len(fields) < 4:
                print '(Bad line from server:', `x`, ')'
                continue
            if len(fields) > 4:
                if fields[4:] != ['+']:
                    print '(Extra info from server: %s)' % (fields[4:])
            else:
                fields.append('')
            fields.insert(0, t)
            url = urltoolsgopher.genURL(fields[3], fields[4], fields[2])
            if t == '1':
                frontier.add(url)
        except:        
            print "error while parsing", repr(x)
            if __debug__:
                raise
