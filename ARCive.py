import re
import time
import md5
import socket
import os.path
import zlib

defaultcreatorid = 'ARCive.py'
defaultcreatorip = '0.0.0.0'

_version_block1_re = re.compile(r'^filedesc://(?P<path>\S+) (?P<versioninfo>.*) (?P<length>\d+)\n$')
_version_block2_re = re.compile(r'^(?P<versionnumber>\d+) (?P<reserved>.*) (?P<origincode>.+)\n$')
_versioninfo_v1_re = re.compile(r'^(?P<ip>[0-9.]+) (?P<date>\d+) text/plain$')
_versioninfo_v2_re = re.compile(r'^(?P<ip>[0-9.]+) (?P<date>\d+) text/plain 200 - - 0 (?P<filename>\S+)$')
_versioninfo_v1003_re = re.compile(r'^(?P<ip>[0-9.]+) (?P<date>\d+) text/plain 200 - - 0 (?P<filename>\S+)$')

# Used to compare file passed
import types
_STRING_TYPES = (types.StringType,)
if hasattr(types, "UnicodeType"):
    _STRING_TYPES = _STRING_TYPES + (types.UnicodeType,)

def  _fromARCdate(s):
    return time.mktime((int(s[0:4]), int(s[4:6]), int(s[6:8]), int(s[8:10]), int(s[10:12]), int(s[12:14]), -1, -1, 0)) - time.timezone

def  _toARCdate(t):
    return time.strftime('%Y%d%m%H%M%S', time.gmtime(t))


class ARCive:
    def __init__(self, file, mode="r", creatorid = defaultcreatorid, creatorip = defaultcreatorip):
        """Open the ARC file with mode read "r", write "w" or append "a"."""
        # code partly taken from zipfile.py
        self.mode = key = mode[0]
        self.creatorid = creatorid
        self.creatorip = creatorip

        # Check if we were passed a file-like object
        if type(file) in _STRING_TYPES:
            self.filename = file
            modeDict = {'r' : 'rb', 'w': 'wb', 'a' : 'r+b'}
            self.fd = open(file, modeDict[mode])
        else:
            self.fd = file
            self.filename = getattr(file, 'name', None)

        if key == 'r':
            self._read_version_block()
        elif key == 'w':
            # write a 'dummy' header
            self._write_header()
        elif key == 'a':
            raise NotImplementedError
        else:
            raise RuntimeError, 'Mode must be "r", "w" or "a"'


    def _parse_version_block1(self):
        """Parse versioninfo for v1"""
        m = _versioninfo_v1_re.match(self.versioninfo)
        if m == None:
            raise RuntimeError, "Not a valid v1 versioninfo header: %r" % self.versioninfo
        self.creatorip = m.group('ip')
        self.creationdate = m.group('date')
        self.urlrecord_re = re.compile(r'^(?P<url>.+) (?P<archiverip>[0-9.]+) (?P<date>\d+) (?P<contenttype>\S+) (?P<length>\d+)\n$') 


    def _parse_version_block2(self):
        """Parse versioninfo for v2"""
        m = _versioninfo_v2_re.match(self.versioninfo)
        if m == None:
            raise RuntimeError, "Not a valid v2 versioninfo header: %r" % self.versioninfo
        self.creatorip = m.group('ip')
        self.creationdate = m.group('date')
        self.creatorfilenmame = m.group('filename') 
        self.urlrecord_re = re.compile(r'^(?P<url>.+) (?P<archiverip>[0-9.]+) (?P<date>\d+) (?P<contenttype>\S+) (?P<resultcode>\d+) (?P<checksum>.+) (?P<location>.+) (?P<offset>\d+) (?P<filename>.+) (?P<length>\d+)\n$') 

    def _parse_version_block1003(self):
        """Parse versioninfo for v1003"""
        m = _versioninfo_v1003_re.match(self.versioninfo)
        if m == None:
            raise RuntimeError, "Not a valid v1003 versioninfo header: %r" % self.versioninfo
        self.creatorip = m.group('ip')
        self.creationdate = m.group('date')
        self.creatorfilenmame = m.group('filename') 
        self.urlrecord_re = re.compile(r'^(?P<url>.+) (?P<archiverip>[0-9.]+) (?P<date>\d+) (?P<contenttype>\S+) (?P<resultcode>\d+) (?P<checksum>.+) (?P<location>.+) (?P<offset>\d+) (?P<filename>.+) (?P<length>\d+) (?P<orglength\d+)\n$') 

    def _read_version_block(self):
        l = self.fd.readline()
        m = _version_block1_re.match(l)
        if m == None:
            raise RuntimeError, "Not a valid arc file header line 1: %r" % l
        self.path = m.group('path')
        self.versioninfo = m.group('versioninfo')
        self.path = m.group('length')
        l = self.fd.readline()
        m = _version_block2_re.match(l)
        if m == None:
            raise RuntimeError, "Not a valid arc file header line 2: %r" % l
        self.version = int(m.group('versionnumber'))
        self.reserved = m.group('reserved')
        self.origincode = m.group('origincode')
        l = self.fd.readline()
        self.recorddefinition = l.strip()
        if self.version == 1:
            pass
            self._parse_version_block1()
        elif self.version == 2:
            pass
            self._parse_version_block2()
        else:
            raise RuntimeError, "unknown arc version: %d" % self.version


    def _write_header(self):
        headerrest = "2 0 %s\nURL IP-address Archive-date Content-type Result-code Checksum Location Offset Filename Archive-length\n" % (self.creatorid)
        self.fd.write("filedesc://%s %s %s text/plain 200 - - 0 %s %d\n%s"  % (os.path.join('', self.filename), self.creatorip, _toARCdate(time.time()), self.filename, len(headerrest), headerrest))

    def close(self):
        self.fd.close()

    def getdir(self):
        self.fd.seek(0)
        self._read_version_block()
        self.dir = {}
        while 1:
            x = self.readdocraw()
            if x == None:
                break
            meta = x[0]
            if meta['url'] not in self.dir:
                self.dir[meta['url']] = []
            self.dir[meta['url']].append((meta['date'], meta['offset']))
        return self.dir

    def writerawdoc(self, data, url, mimetype = 'application/octet-stream', result = 200, location = '-'):
        hash = md5.new(data).hexdigest()
        pos = str(self.fd.tell())
        #data = zlib.compress(data)
        self.fd.write("""\n%s %s %s %s %d %s %s %s %s %s\n""" % (url, self.creatorip, _toARCdate(time.time()), mimetype, result, hash, location, pos, self.filename, len(data)))
        self.fd.write(data)

    def readdocraw(self):
        l = self.fd.readline()
        if l == '':
            return None
        if l != '\n':
            raise RuntimeError, 'invalid doc header line 1: %r' % l 
        l = self.fd.readline()
        m = self.urlrecord_re.match(l)
        if m == None:
            raise RuntimeError, "Not a valid arc doc header line 2: %r" % l 
        meta = m.groupdict()
        meta['length'] = int(m.group('length'))
        meta['date'] = _fromARCdate(m.group('date'))
        data = self.fd.read(meta['length'])
        return(meta, data)


        
if __name__ == '__main__':
    a = ARCive('testN.arc', 'w')
    a.writerawdoc('Xtest1X', 'Xurl1X')
    a.writerawdoc('Xtest2X', 'Xurl2X')
    a.writerawdoc('Xtest3X', 'Xurl3X')
    a.close()
    a = ARCive('test.arc')
    print a.getdir()
    
