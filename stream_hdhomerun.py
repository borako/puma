#!/usr/bin/python

import os, sys, time
import subprocess
import re
from datetime import datetime
import json

# check if process exists
def process_exists(proc, ch):
    ps = subprocess.Popen("ps -ef | grep "+proc+ " | grep " + ch, shell=True, stdout=subprocess.PIPE)
    ps_pid = ps.pid
    output1 = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    output = output1.decode('utf-8')
    for line in output.split("\n"):
        print ( line )
#    if output1 is None:
    for line in output.split("\n"):
        #line = line.decode('utf-8')
        if line != "" and line != None:
            print ("line: " + line )
            fields = line.split()
            if fields[7] == proc:
                return True
    return False

# Transcode and stream HDHomeRun source to HLS
# ch: ch04 ch07 ch12 ch31 etc
# pstarget: udp://192.168.2.x:xxxx
# tunerid: Tuner id (0 or 1) for the HDHomerun unit
# programid: Program ID for the frequency tuned
# homerunid: HDHomeRun unit ID
def run_live(hlsname, pstarget, tunerid, programid, freq, homerunid):
    dirname = os.path.dirname(hlsname)
    hlstime = '10'
    hlssize = '8'
    loglevel = 'debug'
    
    ffmpeg_command = 'ffmpeg -re -i ' + pstarget + '?fifo_size=1000000\&buffer_size=128000' + \
        ' -c:v libx264 -preset veryfast -async 1 -y -vsync 1 -f hls ' + \
        ' -hls_time ' + hlstime + \
        ' -hls_list_size ' + hlssize + \
        ' -hls_flags delete_segments ' + \
        ' -hls_allow_cache 1 ' + \
        hlsname 
        #' -loglevel ' + loglevel 

    homeruncmd1='/usr/local/bin/hdhomerun_config ' + homerunid + ' set /tuner' + tunerid + '/channel auto:' + freq
    homeruncmd2='/usr/local/bin/hdhomerun_config ' + homerunid + ' set /tuner' + tunerid + '/program ' + programid + ' transcode=mobile'
    homeruncmd3='/usr/local/bin/hdhomerun_config ' + homerunid + ' set /tuner' + tunerid + '/target ' + pstarget
    writelog(logfilename, 'Deleting ' + dirname )
    #os.system('rm -f ' + dirname + '/*')
    #subprocess.Popen('rm -f ' + dirname + '/*', shell=True, stdout=subprocess.PIPE)
    subprocess.Popen('rm -f ' + dirname + '/*', shell=True)
    if (os.path.exists(dirname) == False):
        writelog(logfilename, dirname + ' does not exists. Creating...\n')  
        os.makedirs(dirname)
    if (os.path.isfile(hlsname) == False):
        writelog(logfilename, hlsname + ' does not exists. Creating...\n')  
      	os.system('touch ' + hlsname)

    writelog(logfilename, hlsname + ': Starting ffmpeg')
    #os.system(ffmpeg_command + ' &')
    #subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE)
    subprocess.Popen(ffmpeg_command, shell=True)
    # Wait a couple seconds 
    time.sleep (2)
    subprocess.Popen(homeruncmd1, shell=True, stdout=subprocess.PIPE)
    subprocess.Popen(homeruncmd2, shell=True, stdout=subprocess.PIPE)
    subprocess.Popen(homeruncmd3, shell=True, stdout=subprocess.PIPE)

def writelog(logfilename, content):
    f = open (logfilename, 'a')
    f.write (str(datetime.now()) + '|' + content + '\n')
    f.close()
    
logfilename = 'stream.log'
hlsdir = '/mnt/hls/'
jsonfile = '/home/blee/py/channeldic.json'
# Construct informations
with open(jsonfile) as df:
    chstruct = json.load(df)
time1 = [0,0,0,0]
time2 = [0,0,0,0]

# Main loop 
while True:
    for i in range(0, 4):
        if (os.path.isfile(chstruct[i]['hlsname'])):
            time1[i] = os.stat(chstruct[i]['hlsname']).st_mtime
        else:
            time1[i] = 0
            writelog( logfilename, chstruct[i]['hlsname'] + " file does not exist \n")
        if process_exists('ffmpeg', chstruct[i]['ch']) == False:
            writelog( logfilename, chstruct[i]['ch'] + " ffmpeg process does not exist - Starting \n")
            run_live(chstruct[i]['hlsname'], chstruct[i]['pstarget'], chstruct[i]['tunerid'], chstruct[i]['programid'], chstruct[i]['freq'], chstruct[i]['homerunid'])
    time.sleep (30)
    # Now get hls file time and compare to earlier one 
    for i in range(0, 4):
        if (os.path.isfile(chstruct[i]['hlsname'])):
            time2[i] = os.stat(chstruct[i]['hlsname']).st_mtime
            if (time1[i] == time2[i]):
                writelog(logfilename, 'time1: ' + str(time1[i]) + ', time2: ' + str(time2[i]) + "- " + chstruct[i]['ch'] + ' HLS not changed - Restart \n')
                os.system("kill -9 `ps aux | grep ffmpeg | grep " +  chstruct[i]['hlsname'] + " | awk '{print $2}'`")
        else:
            writelog(logfilename, chstruct[i]['ch'] + ' does not exist - Restart\n')
            os.system("kill -9 `ps aux | grep ffmpeg | grep " +  chstruct[i]['hlsname'] + " | awk '{print $2}'`")
