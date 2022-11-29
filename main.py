import tensorflow.lite as tflite
import cv2
import numpy as np

# tensorflow lite
def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}

def capture_image():
    image_path='image/test.jpg'
    img = cv2.imread(image_path)
    img = cv2.resize(img,(224,224))

    return img


def classify_image(image, top_k=1):

  # set mdoel and labels path to use
  labels = load_labels('model/labels.txt')
  interpreter = tflite.Interpreter(model_path='model/model.tflite')

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


def capture_classify(tries=5):
  img = capture_image()
  res, prob = classify_image(img)

  return (res, prob, tries)




def main():
  print(capture_classify())




if __name__ == "__main__":
    main()