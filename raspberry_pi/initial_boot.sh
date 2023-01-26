#!/bin/bash

echo $(date -u) "Delay script execution for 10s" | tee -a log.txt
sleep 10


echo $(date -u) "Chnage directory to raspberry_pi folder." | tee -a log.txt
cd /root/turbiditech-rpi/raspberry_pi/
sleep 2

# echo $(date -u) "Starting to connect to GPRS via GSM module" | tee -a log.txt

# # Initialize the variable to store the IP address
# ip_address=""
# delay=5

# # Run the loop until the IP address is not empty
# while [ -z "$ip_address" ];
# do
#   # Get the IP address
#   ip_address=$(ip address | grep ppp0 | awk '/inet/ {print $2}')

#   # If the IP address is empty, print a message and continue the loop
#   if [ -z "$ip_address" ]; then
#     echo $(date -u) "Unable to retrieve the IP address." | tee -a log.txt
#     sleep 1
#     echo $(date -u) "Closing previous PPP connection." | tee -a log.txt
#     sudo poff rnet > /dev/null
#     sleep $delay
#     sudo kill -HUP 'cat /var/run/ppp0.id'
#     sleep 2
# #    sudo route del default
# #    sleep 2
#     echo $(date -u) "Starting new PPP connection." | tee -a log.txt
#     sudo pon rnet
#     sleep 10
#   fi
# done

# echo $(date -u) "The IP address is $ip_address" | tee -a log.txt
# sleep 2


# destination_ip=$(ifconfig ppp0 | awk '/destination/ {print $6}')
# echo $(date -u) "The destination IP address is $destination_ip" | tee -a log.txt
# sleep 2


# echo $(date -u) "Add 192.168.254.254 destination IP address to default route" | tee -a log.txt
# route del default ppp0
# route del default eth0
# route add default gw 192.168.254.254 ppp0
# sleep 3


echo $(date -u) "Start initial_boot_update.py script" | tee -a log.txt
python3 initial_boot_update.py


sleep 3
echo $(date -u) "Start main.py script" | tee -a log.txt
python3 main.py
