#import picamera
import subprocess
from threading import Thread
from time import time
import ffmpeg
from gps import *
import time
import os
import sys
from datetime import datetime
from datetime import timedelta
try:
    import httplib
except:
    import http.client as httplib


IP_SERVER = "192.168.1.53"

# Wait for the RPi to be ready and running
time.sleep(10)

# Check the camera
if not os.path.exists('/dev/video2'):
    print("Camera error, check its connection.")
    sys.exit(1)

# Connect to the local gpsd
for i in range(0, 10):
    try:
        gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
        break
    except:
        print("GPS error, retrying in 5 seconds.")
        time.sleep(5)

if i > 10:
    print("GPS error, check its connection.")
    sys.exit(1)

os.chdir("/home/pi/records") # Change directory to the records directory


# Ping the host: returns True if it exists, False otherwise
def ping(host):

    # Option for the number of packets as a function of
    #param = '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    #command = ['ping', param, '1', host]

    response = os.system("ping -c1 -w1 " + host + " > /dev/null 2>&1")

    return response == 0


# Run rsync command and check each 20 seconds if the RPi3 is out of range
def sync():
    while True:
        subprocess.call('/usr/bin/flock -n /tmp/cron.lock rsync -vr --remove-source-files -t /home/pi/records/ pi@' + IP_SERVER + ':/home/pi/records', shell=True)
        subprocess.call('find . -type d -empty -delete', shell=True)
        time.sleep(20)
        if not ping(IP_SERVER):
            return

# -framerate 30 -i desktop -filter_complex settb=1/1000,setpts=RTCTIME/1000-1500000000000,mpdecimate,split[out][ts];[out]setpts=N/FRAME_RATE/TB[out] -map [out] -vcodec libx264 -pix_fmt yuv420p -preset fast -crf 0 -threads 0 nodups.mkv -map [ts] -f mkvtimestamp_v2 nodups.txt -vsync 0

# Retrieve gps data (thread)
def write_gps(stamp, gpsd):
    text_file = open(stamp + "/gps.txt", "w")
    time.sleep(3)
    i = 0
    #idk = str(int(round(time.time() * 1000)))
    #k = text_file2.write('{\n    "video_timestamp": ' + idk + '\n}')
    text_file2 = open(stamp + "/meta.json", "w")
    k = text_file2.write('{\n    "video_timestamp": ' + str(int(round(time.time() * 1000))) + '\n}')
    text_file2.close()
    while i<300:
        i += 1
        
        #if i==1: # If it is the first line, write the initial frame timestamp
        while True:
            nx = gpsd.next()
            if nx['class'] == 'TPV':
                break
        
        # For a list of all supported classes and fields refer to: https://gpsd.gitlab.io/gpsd/gpsd_json.html
        
        latitude = getattr(nx,'lat', "Unknown")
        longitude = getattr(nx,'lon', "Unknown")
        speed = getattr(nx,'speed', "Unknown")
        if getattr(nx,'mode', "Unknown") > 1:
            n = text_file.write(str(int(round(time.time() * 1000))) + ' ' + str(latitude) + ' ' + str(longitude) + ' ' + str(speed) + '\n')
        
        # print(int(datetime.timestamp(datetime.fromisoformat(str(packet.time).replace("Z", "+00:00")))))
        # str(i) + ' ' + str(packet.lat) + ' ' + str(packet.lon) + ' ' + str(packet.hspeed) + '\n')
        
        time.sleep(1)
    
    text_file.close()
    os.chdir("/home/pi/records/"+stamp)
    import convert # Convert to visualizer gps data 
    os.chdir("/home/pi/records")
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
# Try to sync first
if ping(IP_SERVER):
    sync()

# MAIN LOOP
while True:
    #camera.split_recording('%d.h264' % ti)
    tday = datetime.today() + timedelta(seconds=3)
    stamp = str(int(tday.strftime('%Y%m%d%H%M%S')))
    #t = Thread(target=gps, args=(stamp, ))
    os.mkdir(stamp)
    t = Thread(target=write_gps, args=(stamp, gpsd, ))
    t.start()
    #ffmpeg.input("/dev/video2", t=300, framerate=15, input_format="h264").output(stamp + '/`date +%s`.txt ' + stamp + '/video.mp4', t=300, f="mkvtimestamp_v2", r=15, codec="copy", bitrate="5M").run()
    subprocess.call("ffmpeg -y -framerate 15 -input_format h264 -t 300 -i /dev/video2 -t 300 -c:v copy " + stamp + "/video.mp4", shell=True)
    # For creating the timestamps.txt ->  -f mkvtimestamp_v2 " + stamp + "/" + str(int(time.time()*1000.0) + 3000) + ".txt"
    t.join()
    if ping(IP_SERVER):
        sync()

    #camera.wait_recording(10)

#camera.stop_recording()


# join all threads
#for t in threads:
#    t.join()

# ffmpeg -y -f v4l2 -video_size 1280x720 -framerate 15 -input_format h264 -i /dev/video2  -filter_complex "settb=1/1000,setpts=RTCTIME/1000-1500000000000,mpdecimate,split[out][ts];[out]setpts=N/FRAME_RATE/TB[out]" -map [out] -vcodec libx264  -preset faster -crf 5 -threads 4 nodups.mp4 -map [ts] -f mkvtimestamp_v2 nodups.txt -vsync 0 
