# rpi
import numpy as np
from time import sleep
from PIL import Image
from tflite_runtime.interpreter import Interpreter
from picamera import PiCamera
from gpiozero import DigitalOutputDevice

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


# obtaining data
def capture_image():
  
  # capture image using PiCamera
  with PiCamera() as camera:
    
    camera.resolution = (300, 300)
    camera.zoom = (0.3, 0.3, 1.0, 1.0)

    # warm up camera
    sleep(3)
    
    # adjusting the blue tint on low light env
    # camera.awb_mode = 'auto'
    camera.drc_strength = 'high'
    camera.image_effect = 'denoise'
    
        
    # preview and capture image
    # camera.start_preview()
    sleep(3)
    camera.capture('../images/test.jpg', quality=100)
    
    # compress image for upload
    im = Image.open("../images/test.jpg")

    # Set the quality to 50 (out of 100)
    im.save("../images/test_compressed.jpg", quality=50, optimize=True)


def read_image(w, h):
  image_path='../images/test.jpg'
  img = Image.open(image_path).convert('RGB')


  # crop image to center
  # frac = 0.70
  # left = img.size[0] * ((1-frac)/2)
  # upper = img.size[1] * ((1-frac)/2)
  # right = img.size[0] - ((1-frac)/2) * img.size[0]
  # bottom = img.size[1] - ((1-frac)/2) * img.size[1]
  # img = img.crop((left, upper, right, bottom))

  img = img.resize((224, 224))
  
  # show image
  # img.show()

  return img


# process data
def load_labels(path):
  with open(path, 'r') as f:
    return [line.strip() for i, line in enumerate(f.readlines())]


def set_input_tensor(interpreter, image):
  # locate the first tensor index from input details
  tensor_index = interpreter.get_input_details()[0]['index']
  
  # return input tensor base on its index
  input_tensor = interpreter.tensor(tensor_index)()[0]
  
  # assing image data to input tensor
  input_tensor[:, :] = image


def unset_input_tensor(interpreter):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  
  # reset input tensors to prevent using same image
  input_tensor[:, :] = np.zeros(shape=(224, 224, 3))


def classify_image(interpreter, image):
  
  # models makes a prediction and store to output tensor
  interpreter.invoke()
  
  output_details = interpreter.get_output_details()[0]
  
  # predicted class label score
  scores = interpreter.get_tensor(output_details['index'])[0]
  
  # dequantized the scores
  scale, zero_point = output_details['quantization']
  scores_dequantized = scale * (scores - zero_point)
  
  #predicted class label probability
  dequantized_max_score = np.max(np.unique(scores_dequantized))
  
  # predicted class label id
  max_score_index = np.where(scores_dequantized == np.max(np.unique(scores_dequantized)))[0][0]
  
  return max_score_index, dequantized_max_score
    

def check_water(retry=3, delay=5):
  label_path = '../model/labels.txt'
  model_path = '../model/model.tflite'

  # set labels
  labels = load_labels(label_path)

  # alternative : from tflite_runtime.interpreter import Interpreter
  # interpreter = tf.lite.Interpreter(model_path)
  interpreter = Interpreter(model_path)

  # print('model loaded successfully')

  # allocate to memory
  interpreter.allocate_tensors()

  # get input details
  _, height, width, _ = interpreter.get_input_details()[0]['shape']
  
  # start loop
  while True:
    result = []
    temp = []
    
    for i in range(retry):

      # capture image using PiCamera
      capture_image()

      # read and resize to np array image
      image = read_image(width, height)

      # initialize data to feed to model
      set_input_tensor(interpreter, image)

      # make predictions
      label_id, prob = classify_image(interpreter, image)

      # getting results
      class_label = labels[label_id].split()[-1]
      accuracy = np.round(prob * 100, 2)

      # collect resutls
      temp.append((class_label, accuracy))

      # reset input tensor
      unset_input_tensor(interpreter)

      sleep(delay)
    
    # check for consitent results
    result = np.unique(list(map(lambda x: x[0], temp))).tolist()
  
    if len(result) == 1:
      avg_accu = np.round(np.mean(list(map(lambda x: x[-1], temp))), 2)
      return result[0], avg_accu
    else:
      print(temp)
      print('invalid results, check again.')


# send / receive data from API
def get_server_status():
  url = f'https://turbiditech.fly.dev/api/device-records/{DEVICE_ID}'
  r = requests.get(url, auth=(EMAIL, PASSWORD))

  if r.status_code == 200:
    data = r.json()[-1]
    v_stat = data['valve_status']
    w_stat = data['water_status']

    return v_stat, w_stat
  else:
    return r.status_code


def get_device_water_status():
  # device water status
  res, prob = check_water(retry=2)
  w_stat = res

  return w_stat, prob


def post_water_valve_status(w_stat, v_stat, prob):

  url = urllib.parse.urlsplit(f'https://turbiditech.fly.dev/api/device-records/{DEVICE_ID}')
  image_path = '../images/test_compressed.jpg'

  details = f'{DEVICE_NAME.upper()} has detected {prob}% {w_stat.upper()} water status. Turning {v_stat.upper()} valve.'

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
  dataList.append(encode(f'{w_stat}'))

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

  dataList.append(encode('--' + boundary))
  dataList.append(encode('Content-Disposition: form-data; name=record_image; filename={0}'.format(image_path)))
  fileType = mimetypes.guess_type(image_path)[0] or 'application/octet-stream'
  dataList.append(encode('Content-Type: {}'.format(fileType)))
  dataList.append(encode(''))

  with open(image_path, 'rb') as f:
      dataList.append(f.read())
      dataList.append(encode('--'+boundary+'--'))
      dataList.append(encode(''))

  body = b'\r\n'.join(dataList)
  payload = body
  headers = {
    'Authorization': f'Basic {b64encode(bytes(f"{EMAIL}:{PASSWORD}", "utf-8")).decode("ISO-8859-1")}',
    'Content-type': f'multipart/form-data; boundary={boundary}'
  }
  conn.request("POST", "/api/device-records/2", payload, headers)
  res = conn.getresponse()

  # data = res.read()

  print(res.status, res.reason)
  
  if res.status == 200:
    print('success sending data.')
  else:
    print('error sending data.')


def main():
  # Create instance for the specified pin
  valve = DigitalOutputDevice(18)

  while True:
    # check server for changes in the valve status
    print('getting data from server')
    server_v_stat, server_w_status = get_server_status()
  

    print(f'valve status manually turned {server_v_stat.upper()}')
    
    # if both server and device valve is OFF
    if (server_v_stat == 'off') and (valve.value == 0):
      valve.off()
      print('both server and device valve status are turned OFF')
      
    # if server valve is OFF and device valve is ON
    if (server_v_stat == 'off') and (valve.value == 1):
      print('user manually turned OFF the valve')
      print('turn valve OFF')
      valve.off()

    # if the valve has been turned on
    # then turn on valve base on check water status results
    if server_v_stat == 'on':
      print('checking water status first')
      device_w_stat, prob = get_device_water_status()

      print(f'device has detected {prob}% {device_w_stat.upper()} water status.')
      
      if (server_w_status == 'clean') and (device_w_stat == 'clean'):
        valve.on()
        print(f'both server and device water status are CLEAN')
      else:
        if device_w_stat == 'clean':
          print('turn valve ON')
          valve.on()
          v_stat = 'on'
        else:
          print('turn valve OFF')
          valve.off()
          v_stat = 'off'

        print('sending results to server')
        post_water_valve_status(w_stat=device_w_stat, v_stat=v_stat, prob=prob)
        

    print('sleep 10 seconds.\n\n')
    sleep(10)





if __name__ == "__main__":
  main()

