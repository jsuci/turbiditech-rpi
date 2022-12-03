import numpy as np
from tflite_runtime.interpreter import Interpreter
from picamera import PiCamera
from fractions import Fraction
from time import sleep
from PIL import Image
from io import BytesIO



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
    

def get_status(retry=3, delay=5):
  label_path = '../model/labels.txt'
  model_path = '../model/model.tflite'

  # set labels
  labels = load_labels(label_path)

  # alternative : from tflite_runtime.interpreter import Interpreter
  interpreter = Interpreter(model_path)
  print('model loaded successfully')

  # allocate to memory
  interpreter.allocate_tensors()

  # get input details
  _, height, width, _ = interpreter.get_input_details()[0]['shape']
  
  # start loop
  while True:
    result = []
    temp = []
    
    for i in range(retry):
      
      print(f'checking {i}')

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



def main():
  res, prob = get_status(retry=2)
  print(res, prob)


if __name__ == "__main__":
  main()

