# opi
import OPi.GPIO as GPIO
from time import sleep


# api
import requests
import os
import http.client
import mimetypes
import urllib.parse
import binascii
from codecs import encode
from base64 import b64encode
from dotenv import load_dotenv


# constants
load_dotenv()
DEVICE_ID = os.getenv('DEVICE_ID')
DEVICE_NAME = os.getenv('DEVICE_NAME')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)



def post_initial_boot_status(v_stat, details):

  url = urllib.parse.urlsplit(f'https://turbiditech.fly.dev/api/device-records/{DEVICE_ID}')

  conn = http.client.HTTPSConnection(url.hostname)
  dataList = []
  boundary = boundary = binascii.hexlify(os.urandom(16)).decode('ascii')

  dataList.append(encode('--' + boundary))
  dataList.append(encode('Content-Disposition: form-data; name=valve_status;'))
  dataList.append(encode('Content-Type: {}'.format('text/plain')))
  dataList.append(encode(''))
  dataList.append(encode(f'{v_stat}'))

  dataList.append(encode('--' + boundary))
  dataList.append(encode('Content-Disposition: form-data; name=water_status;'))
  dataList.append(encode('Content-Type: {}'.format('text/plain')))
  dataList.append(encode(''))
  dataList.append(encode(''))

  dataList.append(encode('--' + boundary))
  dataList.append(encode('Content-Disposition: form-data; name=record_device;'))
  dataList.append(encode('Content-Type: {}'.format('text/plain')))
  dataList.append(encode(''))
  dataList.append(encode(f'{DEVICE_ID}'))

  dataList.append(encode('--' + boundary))
  dataList.append(encode('Content-Disposition: form-data; name=details;'))
  dataList.append(encode('Content-Type: {}'.format('text/plain')))
  dataList.append(encode(''))
  dataList.append(encode(f'{details}'))


  body = b'\r\n'.join(dataList)
  payload = body
  headers = {
    'Authorization': f'Basic {b64encode(bytes(f"{EMAIL}:{PASSWORD}", "utf-8")).decode("ISO-8859-1")}',
    'Content-type': f'multipart/form-data; boundary={boundary}'
  }
  conn.request("POST", f"/api/device-records/{DEVICE_ID}", payload, headers)
  res = conn.getresponse()

  print(res.status, res.reason)
  
  if res.status == 200:
    print('success sending data.')
  else:
    print('error sending data.')


def main():
    # get current device valve status
    if GPIO.input(12) == 1:
        device_v_stat = 'on'
    else:
        device_v_stat = 'off'

    details = f'Initial boot completed. Device is connected the internet. Valve operation set to default state {device_v_stat.upper()}.'
    print(details)

    post_initial_boot_status(device_v_stat, details)



if __name__ == "__main__":
  main()
