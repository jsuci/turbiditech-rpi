#! /bin/bash


cd /home/turbiditech/turbiditech-rpi/raspberry_pi
echo $(date -u) "change directory."

source venv/bin/activate
echo $(date -u) "activate venv"

# Extract the IP address from ip address
net_int=$(ifconfig | grep ppp0)

while [ -z $net_int ]
do
    # Print an error message if no IP address is assigned
    echo $(date -u) "No IP address assigned to PPP connection yet"

#    sudo route del default
#    echo $(date -u) "delete default route" >> /home/turbiditech/log.txt

    sudo poff gprs
    echo $(date -u) "deactivate gprs"

    sleep 5

    sudo pon gprs
    echo $(date -u) "activate gprs"

    # Sleep for 5 seconds before checking again
    sleep 5

    # Extract the IP address from ip address again
    net_int=$(ifconfig | grep ppp0)

done 

# Print the IP address once it has been assigned
echo $(date -u) "Network Interface has been created:  $net_int"

echo $(date -u) "run detection"
while true
do
	python main.py
done

$SHELL
