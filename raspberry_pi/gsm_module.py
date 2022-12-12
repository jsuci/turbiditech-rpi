import serial
from time import sleep


def at_command_exec(ser, com):


  # Send an AT command and read the response
  ser.write(f'{com}\r\n'.encode())
  sleep(5)
  
  # [b'\r\n', b'869988016370054\r\n', b'\r\n', b'OK\r\n']
  response = ser.readlines()
  
  return response
  
  
def main():
  # Open a serial connection to a device with AT commands
  ser = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)
  
  # disable echo
  print(at_command_exec(ser, 'ATE0'))
  
  # product serial number
  print(at_command_exec(ser, 'AT+GSN'))
  
  # Close the serial connection
  ser.close()
  
  
if __name__ == "__main__":
  main()
  
  
