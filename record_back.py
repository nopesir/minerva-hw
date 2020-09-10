import picamera
import subprocess
from threading import Thread
import time
import ffmpeg
import gpsd
import time
import os

# Connect to the local gpsd
gpsd.connect()



# Define a function for the thread
def gps(stamp):
    text_file = open(stamp + "/gps.txt", "w")
    time.sleep(1)
    i = 0
    while i<151:
        i += 1
        packet = gpsd.get_current()
        n = text_file.write(str(i) + ' ' + str(packet.lat) + ' ' + str(packet.lon) + ' ' + str(packet.hspeed) + '\n')
        time.sleep(0.0666667)
    text_file.close()
   #subprocess.call('sudo ffmpeg -y -framerate 15 -i ' + start + ' -r 15 -b:v 5000000 -c:v copy -f mp4 ' + end, shell=True)
   #time.sleep(0.5)
   #subprocess.call(['rm', start])


#camera = picamera.PiCamera(resolution=(1920, 1080), framerate=15)

#first = int(time.time())

#camera.start_recording(str(first)+'.h264', bitrate=5000000)
#camera.wait_recording(10)

threads = []
for i in range(2, 5):
    #camera.split_recording('%d.h264' % ti)
    stamp = str(int(time.time()))
    t = Thread(target=gps, args=(stamp, ))
    os.mkdir(stamp)
    t.start()
    ffmpeg.input("/dev/video2", t=10, framerate=15, input_format="h264").output(stamp + '/video.mp4',t=10, framerate=15, bitrate=5000000, codec="copy").run()
    t.join()
    #camera.wait_recording(10)

#camera.stop_recording()


# join all threads
for t in threads:
    t.join()
