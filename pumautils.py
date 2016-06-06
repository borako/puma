import os, subprocess, signal
from datetime import datetime

# check if process exists. Returns True only if process name matches
# proc: name of the process
# *arg: List of search strings
def process_exists(proc, *arg):
    searchstr = "ps -ef | grep " + proc
    for i in range(len(arg)):
        searchstr += " | grep " + arg[i]
    #ps = subprocess.Popen("ps -ef | grep "+proc+ " | grep " + ch, shell=True, stdout=subprocess.PIPE)
    ps = subprocess.Popen(searchstr, shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    for line in output.split("\n"):
        if line != "" and line != None:
            fields = line.split()
            if fields[7] == proc:
                return True
    return False

# Find and kill process that contains all the strings provided by arg
def kill_proc(*arg):
    searchstr = "ps ax " 
    for i in range(len(arg)):
        searchstr += " | grep " + arg[i]
    searchstr += " | grep -v grep"
    for line in os.popen(searchstr):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)
    return True

# Write log to a file
def writelog(logfilename, content):
    f = open (logfilename, 'a')
    f.write (str(datetime.now()) + '|' + content + '\n')
    f.close()
    return True
    
