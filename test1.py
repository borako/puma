import os,sys

statinfo = os.stat('ch04.sh')

print statinfo
print statinfo.st_mtime

if (os.stat('ch04.sh').st_mtime > 0):
    print 'True'
else:
    print 'False'
