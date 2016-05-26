import subprocess, signal

p1=subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
p2=subprocess.Popen(['grep', 'ffmpeg'], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
out, err = p2.communicate()

i=0
for line in out.splitlines():
    print line + str(i)
    i += 1
'''
    if 'ffmpeg' in line:
        pid = int(line.split(None, 1)[0])
        print ('ffmpeg found: ' + line) 
        print ('Killing PID: ' + str(pid))
        os.kill(pid, signal.SIGKILL)
        '''
