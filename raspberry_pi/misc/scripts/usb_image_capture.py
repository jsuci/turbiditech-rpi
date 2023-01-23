import subprocess
import time

# capture video
duration = 5
cmd = "ffmpeg -f v4l2 -i /dev/video1 -s 320x240 -r 25 -t {} -c:v libx264 -pix_fmt yuv420p -qp 0 -preset fast -y video.mp4".format(duration)
subprocess.run(cmd, shell=True)
time.sleep(5)

# capture image
cmd = "ffmpeg -sseof -3 -i video.mp4 -vsync 0 -q:v 2 -update true -y image.jpg"
subprocess.call(cmd, shell=True)
time.sleep(5)