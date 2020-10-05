import os
import json
import more_itertools as mit
import subprocess


VEL_THRESH = 1.5 #m/s
INTERVAL_THRESH = 4999 #ms

with open("meta.json", "r") as json_file:
    ABSOLUTE_START = int(int((json.load(json_file))['video_timestamp'])/1000)


data = []
with open("gps.txt") as fp: 
    Lines = fp.readlines() 
    for index, line in enumerate(Lines): 
        #print(line)
        line_list = line.replace('\n', '').split(' ')
        #print(line_list)
        data.insert(index, line_list)

groups = []
for group in mit.consecutive_groups([i for i, x in enumerate(data) if float(x[3]) < VEL_THRESH]):
    groups.append([data[index] for index in list(group)])

to_delete = []
for group in groups:
    if (int(group[-1][0]) - int(group[0][0])) > INTERVAL_THRESH: 
        to_delete.append((int(int(group[0][0])/1000), int(int(group[-1][0])/1000)))

print(to_delete)

for i, (start, end) in enumerate(to_delete):
    if (i+1) == len(to_delete):
        print("last is: " + str(start))
        subprocess.call("ffmpeg ", shell=True)
    elif (i+1) == 1:
        print("first is: " + str(start))
        os.chdir("/home/pi/records")

        subprocess
    else:
        
