import cv2
import numpy as np
from keras.models import load_model

def read_image():
    # read image
    image_path='../image/clean-5.jpg'

    # process image to cv2pipfree
    img = cv2.imread(image_path)
    



    # crop image to center
    center = img.shape
    x = center[1]/2 - 224/2
    y = center[0]/2 - 224/2
    img = img[int(y):int(y + 224), int(x):int(x + 224)]

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)

    # show image
    cv2.imshow('Image', img)

    # add wait key. window waits until user presses a key
    cv2.waitKey(0)

    # and finally destroy/close all open windows
    cv2.destroyAllWindows()

    return img

def main():

    read_image()

    # Load the model
    model = load_model('../model/keras_model.h5', compile=False)

    # Grab the labels from the labels.txt file. This will be used later.
    labels = open('../model/labels.txt', 'r').readlines()

    # Grab the webcameras image.
    image = read_image()

    # Resize the raw image into (224-height,224-width) pixels.
    # image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

    # Make the image a numpy array and reshape it to the models input shape.
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

    # Normalize the image array
    image = (image / 127.5) - 1

    # Have the model predict what the current image is. Model.predict
    # returns an array of percentages. Example:[0.2,0.8] meaning its 20% sure
    # it is the first label and 80% sure its the second label.
    probabilities = model.predict(image)

    # Print what the highest value probabilitie label
    print(labels[np.argmax(probabilities)], round(np.max(probabilities)*100,2))



if __name__ == "__main__":
    main()