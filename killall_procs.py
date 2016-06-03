#!/usr/bin/python

import subprocess, signal, os

p=subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
out, err = p.communicate()
proc1 = 'ffmpeg'
proc2 = 'stream_hdhome'
'''
for line in out.splitlines():
    if (proc1 in line) or (proc2 in line):
        pid = int(line.split(None, 1)[0])
        print ('process found: ' + line) 
        print ('Killing PID: ' + str(pid))
        os.kill(pid, signal.SIGKILL)
'''


def kill_proc(*arg):
    searchstr = "ps ax " 
    for i in range(len(arg)):
        searchstr += " | grep " + arg[i]
    searchstr += " | grep -v grep"
    for line in os.popen(searchstr):
        print ("Process to kill: " + line)
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)

kill_proc('ffmpeg')
kill_proc('python', 'stream_hdhomerun')
