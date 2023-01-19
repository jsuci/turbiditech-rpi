import time
from time import sleep
from picamera import PiCamera

frames = 1

camera = PiCamera(resolution=(3280, 2464), framerate=30)
camera.start_preview(resolution=(2600, 2000))
camera.iso = 100

time.sleep(10)

camera.shutter_speed = 8500
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g

start = time.time()
camera.capture_sequence(['test_image%02d.jpg' % i for i in range(frames)])
finish = time.time()
time.sleep(5)
camera.stop_preview()

print('Captured %d frames at %.2ffps' % (    frames,    frames / (finish - start)))
