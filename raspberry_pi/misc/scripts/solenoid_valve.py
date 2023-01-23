import OPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)


while True:
  print('ON valve')
  GPIO.output(12, GPIO.HIGH)
  print('The current value of the pin is', GPIO.input(12))
  print('sleep 5s\n\n')
  sleep(5)


  print('OFF valve')
  GPIO.output(12, GPIO.LOW)
  print('The current value of the pin is', GPIO.input(12))
  print('sleep 5s\n\n')
  sleep(5)

# Cleanup the GPIO settings
GPIO.cleanup()
