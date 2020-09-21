import picamera
import subprocess
from threading import Thread
from time import time
import ffmpeg
import gpsd
import time
import os
import sys
from datetime import datetime
try:
    import httplib
except:
    import http.client as httplib


IP_SERVER = "192.168.1.53"

# Connect to the local gpsd
try:
    gpsd.connect()
except ConnectionRefusedError:
    print("GPS error, check its connection.")
    sys.exit(0)

os.chdir("/home/pi/records") # Change directory to the records directory


# Ping the host: returns True if it exists, False otherwise
def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    #param = '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    #command = ['ping', param, '1', host]

    response = os.system("ping -c1 -w1 " + host + " > /dev/null 2>&1")

    return response == 0


# Run rsync command and check each 20 seconds if the RPi3 is out of range
def sync():
    while True:
        subprocess.call('/usr/bin/flock -n /tmp/cron.lock rsync -vr --remove-source-files /home/pi/records/ pi@' + IP_SERVER + ':/home/pi/records', shell=True)
        subprocess.call('find . -type d -empty -delete', shell=True)
        time.sleep(20)
        if not ping(IP_SERVER):
            return


# Retrieve gps data (thread)
def gps(stamp):
    text_file = open(stamp + "/gps.txt", "w")
    time.sleep(3)
    i = 0
    while i<10:
        i += 1
        packet = gpsd.get_current()
        n = text_file.write(str(int(datetime.timestamp(datetime.fromisoformat(str(packet.time).replace("Z", "+00:00"))))) + ' ' + str(packet.lat) + ' ' + str(packet.lon) + ' ' + str(packet.hspeed) + '\n')
        # print(int(datetime.timestamp(datetime.fromisoformat(str(packet.time).replace("Z", "+00:00")))))
        # str(i) + ' ' + str(packet.lat) + ' ' + str(packet.lon) + ' ' + str(packet.hspeed) + '\n')
        time.sleep(1)
    text_file.close()
   #subprocess.call('sudo ffmpeg -y -framerate 15 -i ' + start + ' -r 15 -b:v 5000000 -c:v copy -f mp4 ' + end, shell=True)
   #time.sleep(0.5)
   #subprocess.call(['rm', start])

'''
#camera = picamera.PiCamera(resolution=(1920, 1080), framerate=15)
#first = int(time.time())
#camera.start_recording(str(first)+'.h264', bitrate=5000000)
#camera.wait_recording(10)
#threads = []
'''

# MAIN LOOP
while True:
    #camera.split_recording('%d.h264' % ti)
    stamp = str(int(datetime.today().strftime('%Y%m%d%H%M%S')) + 3)
    t = Thread(target=gps, args=(stamp, ))
    os.mkdir(stamp)
    t = Thread(target=gps, args=(stamp, ))
    t.start()
    #ffmpeg.input("/dev/video2", t=300, framerate=15, input_format="h264").output(stamp + '/`date +%s`.txt ' + stamp + '/video.mp4', t=300, f="mkvtimestamp_v2", r=15, codec="copy", bitrate="5M").run()
    subprocess.call("ffmpeg -y -framerate 15 -input_format h264 -t 300 -i /dev/video2 -t 300 -c:v copy " + stamp + "/video.mp4 -f mkvtimestamp_v2 " + stamp + "/" + str(int(time.time()+3)) + ".txt", shell=True)
    t.join()
    if ping(IP_SERVER):
        sync()

    #camera.wait_recording(10)

#camera.stop_recording()


# join all threads
#for t in threads:
#    t.join()
