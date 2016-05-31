#!/usr/bin/python

import os, sys, time
import subprocess
import re
from datetime import datetime

# check if process exists
def process_exists(proc, ch):
    ps = subprocess.Popen("ps -ef | grep "+proc+ " | grep " + ch, shell=True, stdout=subprocess.PIPE)
    ps_pid = ps.pid
    output1 = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    output = output1.decode('utf-8')
    for line in output.split("\n"):
        writelog ( '/home/blee/py/python_run_check.log', line )
    for line in output.split("\n"):
        if line != "" and line != None:
            fields = line.split()
            if fields[7] == proc:
                return True
    return False

def writelog(logfilename, content):
    f = open(logfilename, 'a')
    f.write (str(datetime.now()) + '|' + content + '\n')
    f.close()

if process_exists('/usr/bin/python', 'stream_hdhomerun') == False:
    writelog('/home/blee/py/python_run_check.log', 'Python dead - restarting')
    #os.system('python /home/blee/py/stream_hdhomerun.py &')
    subprocess.Popen('/home/blee/py/stream_hdhomerun.py 1', shell=True, stdout=subprocess.PIPE)
#delte cron.log if > 100M in size
cronlog = '/home/blee/py/run-cron.log'
if os.stat(cronlog).st_size > 100000000
    os.remove(cronlog)
