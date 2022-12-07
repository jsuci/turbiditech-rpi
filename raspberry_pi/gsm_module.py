import serial
from time import sleep

# Open a serial connection to a device with AT commands
ser = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)

# Send an AT command and read the response
ser.write(b'AT+GSN\r\n')
sleep(5)
response = ser.readlines()
print(response)  # [b'\r\n', b'869988016370054\r\n', b'\r\n', b'OK\r\n']

# Close the serial connection
ser.close()
