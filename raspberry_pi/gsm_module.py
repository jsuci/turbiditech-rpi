import serial
from time import sleep


def at_command_exec(ser, com):


  # Send an AT command and read the response
  ser.write(f'{com}\r\n'.encode())
  sleep(2)
  
  # [b'\r\n', b'869988016370054\r\n', b'\r\n', b'OK\r\n']
  response = ser.readlines()
  
  return response


def http_get(ser, url):
  
  # Start HTTP service
  ser.write(f'AT+HTTPINIT\r\n'.encode())
  sleep(2)
  
  # HTTP session
  ser.write(f'AT+HTTPPARA="CID",1\r\n'.encode())
  sleep(2)
  ser.write(f'AT+HTTPPARA="URL","{url}"\r\n'.encode())
  sleep(2)
  
  # Start session
  ser.write(f'AT+HTTPACTION=0\r\n'.encode())
  sleep(2)
  stat_resp = ser.readlines()[1]
  
  # Get data
  ser.write(f'AT+HTTPREAD\r\n'.encode())
  sleep(2)
  read_resp = ser.readlines()[1]
  
  return read_resp, stat_resp

def activate_gprs(ser):
  
  # GPRS
  ser.write(f'AT+SAPBR=3,1,"Contype","GPRS"\r\n'.encode())
  sleep(2)
  cont_resp = ser.readlines()[1]
  
  # APN
  ser.write(f'AT+SAPBR=3,1,"APN","internet.globe.com.ph"\r\n'.encode())
  sleep(2)
  apn_resp = ser.readlines()[1]
  
  # Open GPRS Context
  ser.write(f'AT+SAPBR=1,1\r\n'.encode())
  sleep(2)
  open_resp = ser.readlines()[1]
  
  # Check IP
  ser.write(f'AT+SAPBR=2,1\r\n'.encode())
  sleep(2)
  ip_resp = ser.readlines()[1]
  
  if (b'.' in ip_resp):
    print('gprs activated')
  else:
    print('error activating gprs, check if there is enough prepaid credits.')
  
  
  
  
def main():
  # Open a serial connection to a device with AT commands
  ser = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)
  
  # activate gprs
  activate_gprs(ser)
  
  # http get
  http_get(ser, 'https://turbiditech.fly.dev/api/device-records/2')
  
  # Close the serial connection
  ser.close()
  
  
if __name__ == "__main__":
  main()
  
  
