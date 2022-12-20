#! /bin/bash

echo $(date -u) "script has started." >> /home/turbiditech/log.txt
cd raspberry_pi
source venv/bin/activate
sudo pon gprs


while true
do
	python main.py
done
