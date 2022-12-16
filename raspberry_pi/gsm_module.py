import serial
from time import sleep



def activate_gprs(ser):

  # # check IP address
  # ser.write(f'AT+SAPBR=2,1\r\n'.encode())
  # sleep(2)
  # is_valid_ip = ser.readlines()[1]
  
  # if not b'0.0.0.0' in is_valid_ip:
    # print('gprs already attached with IP', is_valid_ip)
  # else:
    # print('gprs not attached, attaching...')
  
  # attach module to GPRS
  ser.write(f'AT+CGATT=1\r\n'.encode())
  sleep(2)
  print(ser.readlines())


  # Set conn type
  ser.write(f'AT+SAPBR=3,1,"Contype","GPRS"\r\n'.encode())
  sleep(2)
  print(ser.readlines())


  # Set the APN
  ser.write(f'AT+SAPBR=3,1,"APN","http.globe.com.ph"\r\n'.encode())
  sleep(2)
  print(ser.readlines())

  # Activate PDP Packet
  ser.write(f'AT+SAPBR=1,1\r\n'.encode())
  sleep(2)
  print(ser.readlines())

  # Query IP address
  ser.write(f'AT+SAPBR=2,1\r\n'.encode())
  sleep(2)
  print(ser.readlines())
  

  
  
  
def http_get(ser):
  

  # Start HTTP service
  ser.write(f'AT+HTTPINIT\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+HTTPINIT')
  
  # Enable SSL
  ser.write(f'AT+HTTPSSL=1\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+HTTPSSL=1')
  
  # Specify connection ID
  ser.write(f'AT+HTTPPARA="CID",1\r\n'.encode())
  sleep(2)
  print(ser.readlines())
  
  # Set Authorization Headers
  ser.write(f'AT+HTTPPARA="CUSTOM","Authorization: Basic anN1Y2kuanN1Y2lAZ21haWwuY29tOmFkbWlu"\r\n'.encode())
  sleep(2)
  print(ser.readlines())
  
  # Set URL parameters
  ser.write(f'AT+HTTPPARA="URL","https://turbiditech.fly.dev/api/device-records/2"\r\n'.encode())
  sleep(2)
  print(ser.readlines())

  
  # Send the request
  ser.write(f'AT+HTTPACTION=0\r\n'.encode())
  sleep(10)
  print(ser.readlines())


  # Read the request
  ser.write(f'AT+HTTPREAD\r\n'.encode())
  sleep(10)
  print(ser.readlines(), 'AT+HTTPREAD')
  
  # Terminate the HTTP service
  ser.write(f'AT+HTTPTERM\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+HTTPTERM')
  

  
  
def main():
  # Open a serial connection to a device with AT commands
  ser = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)
  
  activate_gprs(ser)
  
  http_get(ser)
  

  # Close the serial connection
  ser.close()
  
  
if __name__ == "__main__":
  main()
  
  
