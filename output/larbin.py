#!/usr/bin/python

# $Id$

import os, os.path

class LarbinOutputSystem:
    """Deposits Pages in simple directories saving Meta-Data in a seperate file."""

    def __init__(self, directory):
        """Directory is where to save the oputput."""
        
        self.basename = directory
        if not os.path.exists(self.basename):
            os.makedirs(self.basename)
        self.currentdir = '%06d' % self.findlastdir()
        self.nextdir()


    def findlastdir(self):
        """Find the first dir to write in."""
        maxdir = 0
        for x in os.listdir(self.basename):
            try:
                maxdir = max(maxdir, int(x))
            except:
                pass
        return maxdir


    def nextdir(self):
        cur = int(self.currentdir)
        cur += 1
        self.currentdir = '%06d' % cur  
        os.makedirs(os.path.join(self.basename, self.currentdir))

        self.filecounter = 0
        indexfilepath = os.path.join(self.basename, self.currentdir, 'index.txt')
        self.indexfile = open(indexfilepath, 'w')


    def savePagefile(self, page, fd):
        fd.write(page.getData())


    def save(self, page):
        dummmy, ext = os.path.splitext(page.url)
        if len(ext) > 5:
            ext = ''
        name = os.path.join(self.basename, self.currentdir, 'f%06d' % self.filecounter) + ext.lower()
        fd = open(name, 'w')
        self.indexfile.write('%06d\t%s\n' % (self.filecounter, page.url))
        self.filecounter +=1
        self.indexfile.flush()
        fd.close()
        name = os.path.join(self.basename, self.currentdir, 'm%06d' % self.filecounter)
        fd = open(name, 'w')
        fd.write(str(page.header))
        fd.close()

class LarbinLowMemOutputSystem(LarbinOutputSystem):
    """Avoids reading the whole file into Memory"""

    def savePagefile(self, page, fd):
        # read in chunks
        data = page.read(64000)
        while data:
            fd.write(data)
            data = page.read(64000)
                    

