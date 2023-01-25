#!/bin/bash

cd /root/turbiditech-rpi/raspberry_pi/

echo $(date -u) "Starting to connect to GPRS via GSM module" | tee -a log.txt
# Initialize the variable to store the IP address
ip_address=""
delay=3

# Run the loop until the IP address is not empty
while [ -z "$ip_address" ];
do
  # Get the IP address
  ip_address=$(ip address | grep ppp0 | awk '/inet/ {print $2}')

  # If the IP address is empty, print a message and continue the loop
  if [ -z "$ip_address" ]; then
    echo $(date -u) "Unable to retrieve the IP address." | tee -a log.txt
    sleep $delay
    echo $(date -u) "Close previous PPP connection." | tee -a log.txt
    sudo poff rnet > /dev/null
    sleep $delay
    echo $(date -u) "Delete existing ppp0 gateway." | tee -a log.txt
    sudo route del default ppp0
    echo $(date -u) "Delete existing eth0 gateway." | tee -a log.txt
    sudo route del default eth0
    sleep $delay
    echo $(date -u) "Start new PPP connection." | tee -a log.txt
    sudo pon rnet
    sleep $delay
  fi
done

echo $(date -u) "The IP address is $ip_address" | tee -a log.txt
sleep $delay

echo $(date -u) "Add ppp0 to default route" | tee -a log.txt
sudo route add default ppp0

sleep $delay
echo $(date -u) "Start initial_boot_update.py script" | tee -a log.txt
python3 initial_boot_update.py

sleep $delay
echo $(date -u) "Start main.py script" | tee -a log.txt
python3 main.py