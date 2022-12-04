import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter
# import tensorflow as tf
from time import sleep
from picamera import PiCamera


def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}


def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def classify_image(interpreter, image, labels, top_k=1):

  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

  ordered = np.argpartition(-output, top_k)
  results = [(i, output[i]) for i in ordered[:top_k]]
  label_id, prob = results[0]

  return (labels[label_id], prob)


def capture_image(width=224, height=224):

  # capture image using PiCamera
  with PiCamera() as camera:

    camera.resolution = (500, 500)
    camera.framerate = 24
    camera.start_preview()
    camera.awb_mode = 'fluorescent'
    # camera.contrast = 50
    # camera.brightness = 50
    sleep(2)
    camera.capture('../images/test.jpg')

  # read image
  image_path = '../images/test.jpg'

  # process image to cv2pipfree
  img = cv2.imread(image_path)

  # crop image to center
  center = img.shape
  x = center[1]/2 - width/2
  y = center[0]/2 - height/2
  img = img[int(y):int(y + height), int(x):int(x + width)]

  # convert BGR image to RGB
  # important to get accurate results
  img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

  # resize and interpolate
  img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)

  # show image
  cv2.imshow('Image', img)

  # add wait key. window waits until user presses a key
  cv2.waitKey(0)

  # and finally destroy/close all open windows
  cv2.destroyAllWindows()

  return img


def check_turbidity(tries=5, delay=5):

  labels = load_labels("../model/labels.txt")
  interpreter = Interpreter("../model/model_quantized.tflite")
  interpreter.allocate_tensors()
  _, height, width, _ = interpreter.get_input_details()[0]['shape']

  
  while True:
    result = []
    temp = []
    
    for i in range(tries):
      
      print(f'checking {i}')
      img = capture_image(width, height)
      res, prob = classify_image(interpreter, img, labels)
      temp.append((res, prob))
      sleep(delay)
    
    result = np.unique(list(map(lambda x: x[0], temp))).tolist()
  
    if len(result) == 1:
      print(temp)
      return result[0]
    else:
      print(temp)
      print('inconsistent result, checking again.')


def main():
    
  print(check_turbidity(tries=2))

  # cv2.imshow('image', image)
  # cv2.waitKey(0)
  # cv2.destroyAllWindows()







if __name__ == "__main__":
    main()
