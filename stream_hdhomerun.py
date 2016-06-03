#!/usr/bin/python

import pumautils
import os, sys, time
import subprocess
import re
from datetime import datetime
import json
from pumautils import writelog, process_exists, kill_proc

# Transcode and stream HDHomeRun source to HLS
# ch: ch04 ch07 ch12 ch31 etc
# pstarget: udp://192.168.2.x:xxxx
# tunerid: Tuner id (0 or 1) for the HDHomerun unit
# programid: Program ID for the frequency tuned
# homerunid: HDHomeRun unit ID
#def run_live(hlsname, pstarget, tunerid, programid, freq, homerunid):
def run_live(ch):
    dirname = os.path.dirname(ch['hlsname'])
    hlstime = '10'
    hlssize = '8'
    loglevel = 'debug'
    preset = 'superfast' #ultrafast,superfast, veryfast, faster, fast, medium, slow
    ffmpgcmd = 'ffmpeg -re -i ' + ch['pstarget'] + '?fifo_size=1000000\&buffer_size=128000' + \
        ' -c:v libx264 -preset ' + preset + \
        ' -f hls -hls_time 10 -hls_list_size 8 -hls_flags delete_segments -hls_allow_cache 1 ' + \
        ch['hlsname'] + ' &'
    writelog(logfilename, 'Deleting ' + dirname )
    subprocess.call(["rm", "-f", dirname + "/*"])
    if (os.path.exists(dirname) == False):
        writelog(logfilename, dirname + ' does not exists. Creating...')  
        os.makedirs(dirname)
    if (os.path.isfile(ch['hlsname']) == False):
        writelog(logfilename, ch['hlsname'] + ' does not exists. Creating...')  
      	os.system('touch ' + ch['hlsname'])

    writelog(logfilename, ch['hlsname'] + ': Starting ffmpeg')
    subprocess.Popen(ffmpgcmd, shell=True)
    # Wait a couple seconds 
    time.sleep (2)
    # HDHomerun commands
    subprocess.call(['/usr/local/bin/hdhomerun_config', ch['homerunid'], 'set', '/tuner' + ch['tunerid'] + '/channel', 'auto:'+ch['freq']])
    subprocess.call(['/usr/local/bin/hdhomerun_config', ch['homerunid'], 'set', '/tuner' + ch['tunerid'] + '/program', ch['programid'], 'transcode=mobile'])
    subprocess.call(['/usr/local/bin/hdhomerun_config', ch['homerunid'], 'set', '/tuner' + ch['tunerid'] + '/target', ch['pstarget']])

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
    for i in range(len(chstruct)):
        if (os.path.isfile(chstruct[i]['hlsname'])):
            time1[i] = os.stat(chstruct[i]['hlsname']).st_mtime
        else:
            time1[i] = 0
            writelog( logfilename, chstruct[i]['hlsname'] + " file does not exist")
            if not process_exists('ffmpeg', chstruct[i]['ch']):
                writelog( logfilename, chstruct[i]['ch'] + " ffmpeg process does not exist - Starting ")
                run_live(chstruct[i])
    time.sleep (30)
    # Now get hls file time and compare to earlier one 
    for i in range(len(chstruct)):
        if (os.path.isfile(chstruct[i]['hlsname'])):
            time2[i] = os.stat(chstruct[i]['hlsname']).st_mtime
            # If HLS file has not changed in last 30 seconds, restart
            if (time1[i] == time2[i]):
                writelog(logfilename, 'time1: ' + str(time1[i]) + ', time2: ' + str(time2[i]) + "- " + chstruct[i]['ch'] + ' HLS not changed - Restart')
                kill_proc("ffmpeg", chstruct[i]['hlsname'])
        else:
            writelog(logfilename, chstruct[i]['ch'] + ' does not exist - Restart')
            # Kill FFMPEG process if exists
            kill_proc("ffmpeg", chstruct[i]['hlsname'])
