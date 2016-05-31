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
        if line != "" and line != None:
            fields = line.split()
            if fields[7] == proc:
                return True
    return False

def writelog(logfilename, content):
    f = open(logfilename, 'a')
    f.write (str(datetime.now()) + '|' + content + '\n')
    f.close()

if process_exists('python', 'stream_hdhomerun'):
    writelog('/home/blee/py/python_run_check.log', 'Python process exists')
else:
    writelog('/home/blee/py/python_run_check.log', 'Python dead - restarting')
    os.system('python /home/blee/py/stream_hdhomerun.py')
