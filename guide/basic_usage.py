from tflite_runtime.interpreter import Interpreter
import cv2
import numpy as np


def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}

def main():

    # load custom tflite model
    interpreter = Interpreter(model_path='model/model.tflite')

    # load labels
    labels = load_labels('model/labels.txt')

    # allocate the tensors
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # read and resize the image
    image_path='image/test.jpg'
    img = cv2.imread(image_path)
    img = cv2.resize(img,(224,224))

    # input_details[0]['index'] = the index which accepts the input
    interpreter.set_tensor(input_details[0]['index'], [img])

    # run the inference
    interpreter.invoke()

    # output_details[0]['index'] = the index which provides the output
    output_data = interpreter.get_tensor(output_details[0]['index'])

    # get array of confidence value for each class
    pred = np.squeeze(output_data)

    # get the highest confidence value location
    highest_pred_loc = np.argmax(pred)

    print(labels[highest_pred_loc])

if __name__ == "__main__":
    main()
