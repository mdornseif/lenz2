# $Id: urltoolsgopher.py,v 1.1 2002/01/28 22:26:22 drt Exp $

""" Tools for handling gopher URLs

--drt@un.bewaff.net
"""

def genURL(host, port, selector):

    port = int(port)
    return "gopher://%s:%d/%s" % (host, port, selector)
