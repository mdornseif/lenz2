import gopher        
import monitor
import frontier

from twisted.protocols import protocol
from twisted.internet import main, tcp
from twisted.protocols import telnet
from twisted.python import delay

app = main.Application("lenz2")

factory = protocol.Factory()
factory.protocol = gopher
port = tcp.Port(8070, factory)
app.addPort(port)

# for our debugging pleasure:
ts = telnet.ShellFactory()
ts.username = 'u'
ts.password = 'p'
app.addPort(tcp.Port(8023, ts))

def oop():
    print "oops"

delayed = delay.Delayed()
delayed.loop(monitor.monitor)
app.addDelayed(delayed,)

frontier.addURL('gopher://gopher.quux.org/')
monitor.monitor()


# let's go
app.run()

                
