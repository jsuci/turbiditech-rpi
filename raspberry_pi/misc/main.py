import cv2
import numpy as np

from tflite_runtime.interpreter import Interpreter
from time import sleep
from picamera import PiCamera


# tensorflow lite
def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}


def capture_image():
  # capture image
  with PiCamera() as camera:
    camera.resolution = (500, 500)
    camera.start_preview()
    sleep(2)
    camera.capture('image/test.jpg')
    
  # resize img
  image_path='image/test.jpg'
  img = cv2.imread(image_path)
  img = cv2.resize(img,(224,224))
  
  return img


def classify_image(image, top_k=1):

  # set mdoel and labels path to use
  labels = load_labels('model/labels.txt')
  interpreter = Interpreter(model_path='model/model.tflite')

  # initialize interpreter
  interpreter.allocate_tensors()
  
  # get the required input and output requirements
  input_details = interpreter.get_input_details()[0]
  output_details = interpreter.get_output_details()[0]

  # feed image data to index and run inference
  # if you want to get the details about the image
  # use input_details['shape']
  interpreter.set_tensor(input_details['index'], [image])
  interpreter.invoke()

  # get the results. 
  output = np.squeeze(interpreter.get_tensor(output_details['index']))


  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

  ordered = np.argpartition(-output, top_k)
  results = [(i, output[i]) for i in ordered[:top_k]]

  label_id, prob = results[0]

  return (labels[label_id].split(' ')[-1], float(f'{prob * 100:.2f}'))


def check_turbidity(tries=5, delay=5):
  
  while True:
    result = []
    temp = []
    
    for i in range(tries):
      
      print(f'checking {i}')
      img = capture_image()
      res, prob = classify_image(img)
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
  print(check_turbidity())




if __name__ == "__main__":
    main()
