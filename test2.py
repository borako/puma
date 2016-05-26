hlsdir = '/mnt/hls/'
channels = ['ch04', 'ch07', 'ch09', 'ch31']
hlsnames = []
for i in range(0, 4):
    hlsnames.append(hlsdir + channels[i] + '/' + channels[i] + '.m3u8')
    print hlsnames[i]

for i in range(0, 4):
    print ('channel: ' + channels[i] + ':' + hlsnames[i])
