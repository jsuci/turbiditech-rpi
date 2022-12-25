#!/bin/bash

# Change directory
cd /home/turbiditech/turbiditech-rpi/raspberry_pi/
echo $(date -u) "Change directory" | tee -a log.txt

echo $(date -u) "Activate VENV" | tee -a log.txt
source venv/bin/activate

echo $(date -u) "Start detection loop." | tee -a log.txt
echo "" | tee -a log.txt

python main.py
