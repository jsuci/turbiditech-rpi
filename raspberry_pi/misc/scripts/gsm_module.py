import serial
from time import sleep



def activate_gprs(ser):

  
  # attach module to GPRS
  ser.write(f'AT+CGATT=1\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+CGATT=1')


  # Set conn type
  ser.write(f'AT+SAPBR=3,1,"Contype","GPRS"\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+SAPBR=3,1,"Contype","GPRS"')


  # Set the APN
  ser.write(f'AT+SAPBR=3,1,"APN","http.globe.com.ph"\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+SAPBR=3,1,"APN"...')


  # Activate PDP Packet
  ser.write(f'AT+SAPBR=1,1\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+SAPBR=1,1')

  # Query IP address
  ser.write(f'AT+SAPBR=2,1\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+SAPBR=2,1')
  

  
  
  
def http_get(ser):
  

  # Start HTTP service
  ser.write(f'AT+HTTPINIT\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+HTTPINIT')
  
  
  # Specify connection ID
  ser.write(f'AT+HTTPPARA="CID",1\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+HTTPPARA="CID"')
  
  # Set URL parameters
  ser.write(f'AT+HTTPPARA="URL","www.google.com"\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+HTTPPARA="URL","www.google.com"')

  
  # Send the request
  ser.write(f'AT+HTTPACTION=0\r\n'.encode())
  sleep(10)
  print(ser.readlines(), 'AT+HTTPACTION=0')


  # Read the request
  ser.write(f'AT+HTTPREAD\r\n'.encode())
  sleep(10)
  print(ser.readlines(), 'AT+HTTPREAD')
  
  # Terminate the HTTP service
  ser.write(f'AT+HTTPTERM\r\n'.encode())
  sleep(2)
  print(ser.readlines(), 'AT+HTTPTERM')
  


def activate_ppp(ser):

  # Send the AT command to check the module's response
  ser.write(b'AT\r\n')
  response = ser.read(1024).decode()
  print(response)

  # Set the APN
  ser.write(b'AT+CGDCONT=1,"IP","http.globe.com.ph"\r\n')
  response = ser.read(1024).decode()
  print(response)

  # Set the module to transparent transmission mode
  ser.write(b'AT+CIPMODE=1\r\n')
  response = ser.read(1024).decode()
  print(response)

  # Disable IP header compression
  ser.write(b'AT+CIPCCFG=1,0,0,0,0,0\r\n')
  response = ser.read(1024).decode()
  print(response)

  # Shut down previous connection, if any
  ser.write(b'AT+CIPSHUT\r\n')
  response = ser.read(1024).decode()
  print(response)

  # Establish a PPP connection
  ser.write(b'ATD*99***1#\r\n')
  response = ser.read(1024).decode()
  print(response)

  # Check the status of the connection
  ser.write(b'AT+CPAS\r\n')
  response = ser.read(1024).decode()
  print(response)


  
  
def main():
  # Open a serial connection to a device with AT commands
  ser = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)
  
  activate_ppp(ser)

  # Close the serial connection
  # ser.close()
  
  
if __name__ == "__main__":
  main()
  
  
