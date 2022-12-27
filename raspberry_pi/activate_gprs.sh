#!/bin/bash

# Initialize the variable to store the IP address
ip_address=""

# Run the loop until the IP address is not empty
while [ -z "$ip_address" ];
do
  # Get the IP address
  ip_address=$(ip address | grep ppp0 | awk '/inet/ {print $2}')

  # If the IP address is empty, print a message and continue the loop
  if [ -z "$ip_address" ]; then
    echo $(date -u) "Unable to retrieve the IP address." | tee -a log.txt
    sleep 5
    echo $(date -u) "Closing previous PPP connection." | tee -a log.txt
    sudo poff rnet > /dev/null
    sleep 5
    sudo kill -HUP 'cat /var/run/ppp0.pid'
    sleep 5
    sudo route del default
    sleep 5
    echo $(date -u) "Starting new PPP connection." | tee -a log.txt
    sudo pon rnet
    sleep 5
  fi
done

echo $(date -u) "The IP address is $ip_address" | tee -a log.txt
