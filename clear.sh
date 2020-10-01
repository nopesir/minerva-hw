#!/bin/bash

for D in `find /home/pi/records -mindepth 1 -maxdepth 1 -type d`
do
    FILE="$D/visualizer.txt"
    if [ ! -f "$FILE" ]; then
        `rm -R $D`
fi
done
