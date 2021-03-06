#!/usr/bin/python

# $Id$

import os, os.path

class LarbinOutputSystem:
    """Deposits Pages in simple directories saving Meta-Data in a seperate file."""

    def __init__(self, directory, maxfilesperdir = 2000):
        """Directory is where to save the oputput."""
        self.maxfilesperdir = maxfilesperdir 
        self.basename = directory
        if not os.path.exists(self.basename):
            os.makedirs(self.basename)
        self.currentdir = 'd%06d' % self.findlastdir()
        self.nextDir()


    def findlastdir(self):
        """Find the first dir to write in."""
        maxdir = 0
        for x in os.listdir(self.basename):
            try:
                maxdir = max(maxdir, int(x))
            except:
                pass
        return maxdir


    def nextDir(self):
        while 1:
            cur = int(self.currentdir)
            cur += 1
            self.currentdir = '%06d' % cur
            if not os.path.exists(os.path.join(self.basename, self.currentdir)):
                os.makedirs(os.path.join(self.basename, self.currentdir))
                break

        self.filecounter = 0
        indexfilepath = os.path.join(self.basename, self.currentdir, 'index.txt')
        self.indexfile = open(indexfilepath, 'w')
        self.indexfile.write('#\n')


    def savePagefile(self, page, fd):
        fd.write(page.body)


    def save(self, page):
        dummmy, ext = os.path.splitext(page.url)
        if len(ext) > 5:
            ext = ''
        name = os.path.join(self.basename, self.currentdir, 'f%06d' % self.filecounter) + ext.lower()
        fd = open(name, 'w')
        self.savePagefile(page, fd)
        self.indexfile.write('%06d\t%s\n' % (self.filecounter, page.url))
        self.filecounter +=1
        self.indexfile.flush()
        fd.close()
        name = os.path.join(self.basename, self.currentdir, 'm%06d' % self.filecounter)
        fd = open(name, 'w')
        fd.write(str(page.header))
        fd.close()

        if self.filecounter > self.maxfilesperdir:
            self.nextDir()

class LarbinLowMemOutputSystem(LarbinOutputSystem):
    """Avoids reading the whole file into Memory"""

    def savePagefile(self, page, fd):
        # read in chunks
        data = page.read(64000)
        while data:
            fd.write(data)
            data = page.read(64000)
                    

