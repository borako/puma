import subprocess, signal, os

p=subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
out, err = p.communicate()

for line in out.splitlines():
    if 'ffmpeg' in line:
        pid = int(line.split(None, 1)[0])
        print ('ffmpeg found: ' + line) 
        print ('Killing PID: ' + str(pid))
        os.kill(pid, signal.SIGKILL)
