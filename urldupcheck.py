# $Id: urldupcheck.py,v 1.1 2002/01/28 22:26:22 drt Exp $

"""check if a url was already crawled

  --drt@un.bewaff.net
"""

# python needs sets!
db = {}

def isDup(data):
    if db.has_key(data):
        return 1
    else:
        # I want sets in Python!
        db[data] = None
        return None
