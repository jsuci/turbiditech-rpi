# from gpiozero import DigitalOutputDevice, LED
# from time import sleep
# import RPi.GPIO as GPIO

# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)

# GPIO.setup(18, GPIO.OUT)

# while True:
  # print('opening valve')
  # GPIO.output(18, 1)
  # print('sleep')
  # sleep(10)
  # print('closing valve')
  # GPIO.output(18, 0)
  # sleep(10)

from gpiozero import DigitalOutputDevice
from time import sleep

valve = DigitalOutputDevice(18)

while True:
  print('ON valve')
  valve.on()
  print('sleep 5s')
  sleep(5)
  print('OFF valve')
  valve.off()
  print('sleep 5s')
  sleep(5)
