import picamera
import subprocess
from threading import Thread
import time

# Define a function for the thread
def convert(name):
   start = str(name) + '.h264'
   end = str(name) + '.mp4'
   subprocess.call(['ffmpeg', '-y', '-framerate', '15', '-i', start, '-r', '15', '-b:v', '5000000', '-c:v', 'copy', '-f', 'mp4', end])
   subprocess.call(['rm', start])


camera = picamera.PiCamera(resolution=(1920, 1080), framerate=15)
camera.start_recording(str(int(time.time()))+'.h264', bitrate=5000000)
camera.wait_recording(20)

threads = []
for i in range(2, 11):
    ti = int(time.time())
    camera.split_recording('%d.h264' % ti)
    t = Thread(target=convert, args=(str(ti), ))
    t.start()
    threads.append(t)
    camera.wait_recording(20)

camera.stop_recording()


# join all threads
for t in threads:
    t.join()
