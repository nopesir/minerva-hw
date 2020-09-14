import picamera
import subprocess
from threading import Thread
import time
import ffmpeg
import gpsd
import time
import os
import sys
try:
    import httplib
except:
    import http.client as httplib



# Connect to the local gpsd
try:
    gpsd.connect()
except ConnectionRefusedError:
    print("GPS error, check its connection.")
    sys.exit(0)

os.chdir("/home/pi/records")
def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


def sync():
    subprocess.call('rsync -vr --remove-source-files /home/pi/records/ pi@192.168.1.53:/home/pi/records', shell=True)
    subprocess.call('find . -type d -empty -delete', shell=True)
    while True:
        time.sleep(20)
        if not ping("192.168.1.53"):
            return


# Define a function for the thread
def gps(stamp):
    text_file = open(stamp + "/gps.txt", "w")
    time.sleep(3)
    i = 0
    while i<1800:
        i += 1
        packet = gpsd.get_current()
        n = text_file.write(str(i) + ' ' + str(packet.lat) + ' ' + str(packet.lon) + ' ' + str(packet.hspeed) + '\n')
        time.sleep(0.06667)
    text_file.close()
   #subprocess.call('sudo ffmpeg -y -framerate 15 -i ' + start + ' -r 15 -b:v 5000000 -c:v copy -f mp4 ' + end, shell=True)
   #time.sleep(0.5)
   #subprocess.call(['rm', start])


#camera = picamera.PiCamera(resolution=(1920, 1080), framerate=15)

#first = int(time.time())

#camera.start_recording(str(first)+'.h264', bitrate=5000000)
#camera.wait_recording(10)

#threads = []
while True:
    #camera.split_recording('%d.h264' % ti)
    stamp = str(int(time.time())+3)
    t = Thread(target=gps, args=(stamp, ))
    os.mkdir(stamp)
    t.start()
    ffmpeg.input("/dev/video2", t=120, framerate=15, input_format="h264").output(stamp + '/video.mp4',t=120, framerate=15, bitrate=5000000, codec="copy").run()
    t.join()
    if ping("192.168.1.53"):
        sync()

    #camera.wait_recording(10)

#camera.stop_recording()


# join all threads
#for t in threads:
#    t.join()
