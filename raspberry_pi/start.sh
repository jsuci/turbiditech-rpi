cd /home/turbiditech/turbiditech-rpi/raspberry_pi/

while :
do
  sleep 10

  bash activate_gprs.sh

  sleep 5

  bash activate_script.sh
done
