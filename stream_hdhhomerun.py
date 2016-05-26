import os, sys, time
import subprocess
import re

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

    homeruncmd1='hdhomerun_config ' + homerunid + ' set /tuner' + tunerid + '/channel auto:' + freq
    homeruncmd2='hdhomerun_config ' + homerunid + ' set /tuner' + tunerid + '/program ' + programid + ' transcode=mobile'
    homeruncmd3='hdhomerun_config ' + homerunid + ' set /tuner' + tunerid + '/target ' + pstarget

    if (os.path.exists(dirname) == False):
      os.makedirs(dirname)
    if (os.path.isfile(hlsname) == False):
      os.system('touch ' + hlsname)

    os.system(ffmpeg_command + ' &')
    # Wait a couple seconds 
    time.sleep (2)
    os.system(homeruncmd1)
    os.system(homeruncmd2)
    os.system(homeruncmd3)

hlsdir = '/mnt/hls/'
# Construct informations
chstruct = []
chstruct.append({"ch":"ch04", "pstarget":"udp://192.168.2.50:5003", "freq":"599000000", "homerunid":"1052C840", "tunerid":"0", "programid":"1", "hlsname":"/mnt/hls/ch04/ch04.m3u8"})
chstruct.append({"ch":"ch07", "pstarget":"udp://192.168.2.50:5002", "freq":"177000000", "homerunid":"1052982E", "tunerid":"1", "programid":"3", "hlsname":"/mnt/hls/ch07/ch07.m3u8"})
chstruct.append({"ch":"ch09", "pstarget":"udp://192.168.2.50:5001", "freq":"189000000", "homerunid":"1052982E", "tunerid":"0", "programid":"1", "hlsname":"/mnt/hls/ch09/ch09.m3u8"})
chstruct.append({"ch":"ch31", "pstarget":"udp://192.168.2.50:5004", "freq":"581000000", "homerunid":"1052C840", "tunerid":"1", "programid":"3", "hlsname":"/mnt/hls/ch31/ch31.m3u8"})
# Used for stagnant m3u8 (may not be needed since we reeencode now)
time1 = [0,0,0,0]
time2 = [0,0,0,0]
# Main loop 
while True:
  for i in range(0, 4):
    if (os.path.isfile(chstruct[i]['hlsname'])):
      time1[i] = os.stat(chstruct[i]['hlsname']).st_mtime
    if process_exists('ffmpeg', chstruct[i]['ch']) == False:
      print (chstruct[i]['ch'] + "not running - Start")
      run_live(chstruct[i]['hlsname'], chstruct[i]['pstarget'], chstruct[i]['tunerid'], chstruct[i]['programid'], chstruct[i]['freq'], chstruct[i]['homerunid'])
  time.sleep (30)
  # Now get hls file time and compare to earlier one 
  for i in range(0, 4):
    if (os.path.isfile(chstruct[i]['hlsname'])):
        time2[i] = os.stat(chstruct[i]['hlsname']).st_mtime
        if (time1[i] == time2[i]):
          print ('HLS not changed - restart')
          os.system("kill -9 `ps aux | grep ffmpeg | grep " +  chstruct[i]['hlsname'] + " | awk '{print $2}'`")
