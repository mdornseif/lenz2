#!/bin/sh
find . -type f -exec gmd5dum {} \; | uniq -w 32 sums.2 | cut -c 35-999 | xargs rm
