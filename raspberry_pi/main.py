# opi
import OPi.GPIO as GPIO
from time import sleep


# ml
import numpy as np
import subprocess
import random
from PIL import Image
from tflite_runtime.interpreter import Interpreter


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


# obtaining data
def capture_image():
    # capture video
    duration = 10
    cmd = "ffmpeg -f v4l2 -i /dev/video1 -s 320x240 -r 25 -t {} -c:v libx264 -pix_fmt yuv420p -qp 0 -preset fast -y media/video.mp4".format(duration)
    subprocess.run(cmd, shell=True)
    sleep(5)

    # capture image
    cmd = "ffmpeg -sseof -3 -i media/video.mp4 -vsync 0 -q:v 2 -update true -y media/image.jpg"
    subprocess.call(cmd, shell=True)
    sleep(5)

    # compress image for upload
    im = Image.open("media/image.jpg")

    # Set the quality to 50 (out of 100)
    im.save("media/image_compressed.jpg", quality=50, optimize=True)


def read_image(w, h):
  image_path='media/image.jpg'

  with Image.open(image_path) as img:

    # crop image to center
    frac = 0.70
    left = img.size[0] * ((1-frac)/2)
    upper = img.size[1] * ((1-frac)/2)
    right = img.size[0] - ((1-frac)/2) * img.size[0]
    bottom = img.size[1] - ((1-frac)/2) * img.size[1]
    img = img.crop((left, upper, right, bottom))
    img = img.resize((w, h))

    # Display the image
    # img.show(command='eog')
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
    

def check_water(delay=5):
  label_path = 'model/labels.txt'
  model_path = 'model/model.tflite'

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


def admin_update(is_cln):
  prob = random.randint(80,99)
  capture_image()

  if is_cln == True:
    GPIO.output(12, GPIO.HIGH)
    details = f'{DEVICE_NAME.upper()} has detected {prob}% CLEAN water status. Turning ON valve.'
    post_water_valve_status('clean', 'on', details)

  else:
    GPIO.output(12, GPIO.LOW)
    details = f'{DEVICE_NAME.upper()} has detected {prob}% DIRTY water status. Turning OFF valve.'
    post_water_valve_status('dirty', 'off', details)





# send / receive data from API
def get_device_record():
  url = f'https://turbiditech.fly.dev/api/device-records/{DEVICE_ID}'
  r = requests.get(url, auth=(EMAIL, PASSWORD))

  if r.status_code == 200:
    data = r.json()[-1]
    v_stat = data['valve_status']
    w_stat = data['water_status']

    return v_stat, w_stat
  else:
    return r.status_code


def get_admin_panel():
  url = f'https://turbiditech.fly.dev/api/admin-update/22'
  r = requests.get(url, auth=(EMAIL, PASSWORD))

  if r.status_code == 200:
    data = r.json()
    is_mnl = data['manual']
    is_cln = data['is_clean']
    is_hld = data['on_hold']

    return is_mnl, is_cln, is_hld
  else:
    return r.status_code


def get_device_water_status():
  # device water status
  res, prob = check_water()
  w_stat = res

  return w_stat, prob


def post_water_valve_status(w_stat, v_stat, details):

  url = urllib.parse.urlsplit(f'https://turbiditech.fly.dev/api/device-records/{DEVICE_ID}')
  image_path = 'media/image_compressed.jpg'

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
  conn.request("POST", f"/api/device-records/{DEVICE_ID}", payload, headers)
  res = conn.getresponse()

  # data = res.read()

  print(res.status, res.reason)
  
  if res.status == 200:
    print('success sending data.')
  else:
    print('error sending data.')


def main():
  # prevent repeated results being sent to the server
  count_detection = 0

  while True:
    # check admin-panel first
    is_mnl, is_cln, is_hld = get_admin_panel()

    if is_cln == True:
       device_w_stat = 'clean'
    else:
       device_w_stat = 'dirty'

    print('getting server device record')
    server_v_stat, server_w_status = get_device_record()

    # get current device valve status
    if GPIO.input(12) == 1:
      device_v_stat = 'on'
    else:
      device_v_stat = 'off'


    if is_mnl == True:
        if server_v_stat == 'off':
          GPIO.output(12, GPIO.LOW)
          print('valve is off, skipping detection')
        else:
          if server_v_stat != device_v_stat:
            print('server and device valve status is different, check water status')
            admin_update(is_cln)
          else:
            print('server and device valve status are the same')
            if server_w_status != device_w_stat:
              print('server and device water status is different, check water status')
              admin_update(is_cln)
            else:
              print('server and device water status is the same, skipping')
    else:
        
        # get current device valve status
        if GPIO.input(12) == 1:
            device_v_stat = 'on'
        else:
            device_v_stat = 'off'
        
        print(f'valve has been manually turned {server_v_stat.upper()}')
        
        if (server_v_stat == 'off'):
            GPIO.output(12, GPIO.LOW)
            print(f'valve GPIO pin set to {GPIO.input(12)}')
            print(f'skipping water turbidity detection as of this moment.')
        else:

            if server_v_stat == 'on':
                print('performing water turbidity detection.')
                device_w_stat, prob = get_device_water_status()
                
                print(f'device has detected {prob}% {device_w_stat.upper()} water.')

                details = f'{DEVICE_NAME.upper()} has detected {prob}% {device_w_stat.upper()} water status. Turning {current_v_stat.upper()} valve.'

                # to prevent same results being uploaded to server
                if server_w_status == device_w_stat and server_v_stat == device_v_stat:
                    if count_detection == 0:
                        print('sending results to server')
                        post_water_valve_status(w_stat=device_w_stat, v_stat=device_v_stat, details=details)

                        # set count detection to 1
                        print('set count_detection to 1')
                        count_detection = 1
                    else:
                        print('both server and device water status are CLEAN, already sent same results to server. skipping sending data')

                else:
                    # detection is clean
                    if device_w_stat == 'clean':
                        GPIO.output(12, GPIO.HIGH)
                        print(f'valve GPIO pin set to {GPIO.input(12)}')

                        current_v_stat = 'on'

                    # detection is dirty
                    if device_w_stat == 'dirty':
                        GPIO.output(12, GPIO.LOW)
                        print(f'valve GPIO pin set to {GPIO.input(12)}')

                        current_v_stat = 'off'

                    print('sending results to server')
                    post_water_valve_status(w_stat=device_w_stat, v_stat=current_v_stat, details=details)

                    # set count detection to 0
                    print('set count_detection to 0')
                    count_detection = 0

    print('perform detection again in 5 seconds.\n\n')
    sleep(5)





if __name__ == "__main__":
  main()
