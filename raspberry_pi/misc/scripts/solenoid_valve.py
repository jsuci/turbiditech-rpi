#from gpiozero import DigitalOutputDevice
#from time import sleep
#
#valve = DigitalOutputDevice(14)

import OPi.GPIO as GPIO
from time import sleep

# Set the pin numbering mode
GPIO.setmode(GPIO.BOARD)

# Set pin 12 as an output pin
GPIO.setup(11, GPIO.OUT)





while True:
  print('ON valve')
  GPIO.output(11, GPIO.HIGH)
  print('The current value of the pin is', GPIO.input(11))
  print('sleep 5s\n\n')
  sleep(5)


  print('OFF valve')
  GPIO.output(11, GPIO.LOW)
  print('The current value of the pin is', GPIO.input(11))
  print('sleep 5s\n\n')
  sleep(5)

# Cleanup the GPIO settings
GPIO.cleanup()
