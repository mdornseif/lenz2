# --drt@un.bewaff.net - http://c0re.jp/

db = {}

def getInfo():
    return ("dupecheck", ['dupecheck database size %d entries' % len(db)])


def checkIfOkAndAdd(key):
    """If key is already in db return 0, else add key and return 1."""
    if key in db:
        return 0
    else:
        db[key] = 1
        return 1


def test():
    verbose = 1
    import bsddb
    openmethod = bsddb.hashopen

    if verbose:
        print '\nTesting: ', what

    fname = tempfile.mktemp()
    f = openmethod(fname, 'c')
    verify(f.keys() == [])
    if verbose:
        print 'creation...'
    f['0'] = ''
    f['a'] = 'Guido'
    f['b'] = 'van'
    f['c'] = 'Rossum'
    f['d'] = 'invented'
    f['f'] = 'Python'
    if verbose:
        print '%s %s %s' % (f['a'], f['b'], f['c'])

    if what == 'BTree' :
        if verbose:
            print 'key ordering...'
        f.set_location(f.first()[0])
        while 1:
            try:
                rec = f.next()
            except KeyError:
                if rec != f.last():
                    print 'Error, last != last!'
                f.previous()
                break
            if verbose:
                print rec
        if not f.has_key('a'):
            print 'Error, missing key!'

    f.sync()
    f.close()
    if verbose:
        print 'modification...'
    f = openmethod(fname, 'w')
    f['d'] = 'discovered'

    if verbose:
        print 'access...'
    for key in f.keys():
        word = f[key]
        if verbose:
            print word

    f.close()
    try:
        os.remove(fname)
    except os.error:
        pass

if __name__ == '__main__':
    test()
