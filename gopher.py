#!python
# Time-stamp: <02/02/17 20:08:36 drt@un.bewaff.net>

"""Gopher Protocol implementation.

for twisted 0.15.0

See RfC 1436 and http://iubio.bio.indiana.edu/soft/util/gopher/Gopher+-spec.text

  --drt@un.bewaff.net - http://c0re.jp/
"""

# Is support for Gopher+ worth all the work? Does anybody need or want this?

import string
from twisted.protocols import protocol
from twisted.protocols import basic
from cStringIO import StringIO

# types returned by gopher servers                                      
FILE            = '0'   # Item is a (text) file
DIRECTORY       = '1'   # Item is a directory 
CSOPHONEBOOK    = '2'   # Item is a CSO phone-book server
ERROR           = '3'   # Error
BINHEX          = '4'   # Item is a BinHexed Macintosh file.
DOSBIN          = '5'   # Item is DOS binary archive of some sort.
                        # Client must read until the TCP connection closes.  Beware.
UUENCODE        = '6'   # Item is a UNIX uuencoded file.
SEARCHSERVER    = '7'   # Item is an Index-Search server.
TELNET          = '8'   # Item points to a text-based telnet session.
BINARY          = '9'   # Item is a binary file!
                        # Client must read until the TCP connection closes.  Beware.
REDUNDANTSERVER = '+'   # Item is a redundant server
TN3270          = 'T'   # Item points to a text-based tn3270 session.
GIF             = 'g'   # Item is a GIF format graphics file.
IMAGE           = 'I'   # Item is some kind of image file.  Client decides how to display.
UNKNOWN         = '?'   
BITMAP          = ':'   # Gopher+ Bitmap response
MOVIE           = ';'   # Gopher+ Movie response
SOUND           = '<'   # Gopher+ Sound response
# Seen in the Wild
HTML            = 'h'   # WWW-stuff
INFO            = 'i'   # Greeting / BLURB

# textual description
responses = { FILE            : 'File',
              DIRECTORY       : 'Directory',
              CSOPHONEBOOK    : 'CSO phone-book server',
              ERROR           : 'Error',
              BINHEX          : 'BinHexed Macintosh file',
              DOSBIN          : 'DOS binary archive',
              UUENCODE        : 'UNIX UUEncoded file',
              SEARCHSERVER    : 'Index-Search server',
              TELNET          : 'Telnet session',
              BINARY          : 'Binary File',
              REDUNDANTSERVER : 'Redundant server',
              TN3270          : 'tn3270 session',
              GIF             : 'GIF File',
              IMAGE           : 'Image File',
              UNKNOWN         : 'Unknown Data',   
              BITMAP          : 'Bitmap Image',
              MOVIE           : 'Movie',
              SOUND           : 'Sound',
              HTML            : 'HTML File',
              INFO            : 'Blurb'
              }

# Filetypes which will not end with a footer, not used anywhere for now 
binary = [DOSBIN, BINARY, GIF, IMAGE, UNKNOWN, BITMAP, MOVIE, SOUND]


class gopherClient(basic.LineReceiver):
    """A client for the Gopher (RfC 1436) Protocol.

    This particular implementation reads the whole response into
    memory. You might think about changing rawDataReceived to write
    directly to disk, if you expect to recive multi-megabyte binary
    files."""
    # TODO: support for ASK
    # TODO: Searching support
    
    def __init__(self, selector = '', binary = 0):
        """Create a gopher client instance.

        The optional Parameter indicates that you await binary date like '5', '9', 'I' and 'g'
        """
        self.selector = selector
        self.binary = binary
        self.__buffer = []
        self.selectorSend = 0
        self.transmissionFinished = 0
  
    def lineReceived(self, line):
        """Called by the event-loop whenever data in line mode is recive."""
        if self.transmissionFinished:
            # the server still sends data - is this a problem?
            raise runtimeError, "Server is sending still data after EOT marker."
        if line == '.':
            # the server finished sending data, close connection
            self.transport.loseConnection()
            self.transmissionFinished = 1
        else:
            self.__buffer.append(line)
    
    def rawDataReceived(self, data):
        """Called by the event-loop whenever data in raw mode is recive.

        This is used for binary transmission"""
        # we don't have to detect the end of the data like in line mode
        # since the server simply will close the connection when in binary
        # mode
        self.__buffer.append(data)
   
    def connectionLost(self):
        """Called when the connection is closed."""
        if not binary:
            # with non binary Data we have to strip the EOD marker
            pos = rfind(self.__buffer, "\r\n.\r\n")
            if pos == -1:
                # No EOD marker - how to handle that?
                pass
            else:
                self.__buffer = self.__buffer[0:pos]                               
        self.handleResponse(self.__buffer)

    def connectionMade(self):
        """Called when connection succeeded, initiated sending of selector."""
        self.sendSelector(self.selector)

    def sendSelector(self, selector):
        """Send a selector to request data from the server."""
        if self.selectorSend:
            raise runtimeError, "Selector (%r) can't be send twice." % (selector) 
        self.transport.write('%s\r\n' % (selector))
        self.selectorSend = 1
        if self.binary:
            self.setRawMode()

    def handleResponse(self, buffer):
        """This is called when the transmission is finished.

        Mustbe overwritten by the user. Buffer contains a list of data
        chunks recived by the server. In non-binary mode data chunks
        are actually lines."""
        raise NotImplementedError, repr(buffer);
    

class gopher(basic.LineReceiver):
    """A receiver for gopher requests.
    """
    selector = None

    def __init__(self):
        pass
    
    def lineReceived(self, line):
        # This should be called only once since the client SHOULD send
        # only a single line

        # gopher+ clients might send more than a simple selector. For
        # now we just ignore it.
        line = line.split('\t')[0]
        self.selector = line
        self.selectorReceived(line)

    def selectorReceived(self, selector):
        """Do pre-processing (for content-length) and store this header away.
        """

        # dummy
        self.transport.write('iThis is a dummy Server, you selected %r\tfake\t(NONE)\t\r\n1Test\tfake\t(NONE)\t\r\n.\r\n' % (selector))
        self.transport.loseConnection()


# This is example code
if __name__ == '__main__':
    from twisted.protocols import protocol
    from twisted.internet import main, tcp

    # a application instance is the framework which holds its all together
    app = main.Application("gopher-demo")

    # gopherRequestor class is derived from gopherClient
    # but takes the selector string in the constructor
    # and prints out the response to stdout
    class gopherRequestor(gopherClient):
        def __init__(self, selector = '', binary = 0):
            self.selector = selector
            gopherClient.__init__(self, binary)

        def connectionMade(self):
            self.sendSelector(self.selector)

        def handleResponse(self, buffer):
            print repr(buffer)

    # create a TCP client connection 
    tcp.Client('gopher.quux.org', 70, gopherRequestor())

    # start a gopher-server just for the fun of it
    factory = protocol.Factory()
    factory.protocol = gopher
    port = tcp.Port(8070, factory)
    app.addPort(port)

    # run all the stuff
    app.run()

    # This should output the directory of gopher.quux.org and then sit
    # there serving gopher requests at port 8070. Try
    # gopher://localhost:8070/TeSt
                
