#!/bin/sh
find pages documents -type f -exec gmd5sum {} \; | guniq -w 32 -d | cut -c 35-999 | xargs rm
