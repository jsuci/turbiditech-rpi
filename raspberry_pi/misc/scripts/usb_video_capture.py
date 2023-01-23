import subprocess
import time

# The duration of the video
duration = 20

# The command to execute
cmd = "ffmpeg -f v4l2 -i /dev/video1 -s 320x240 -r 25 -t {} -c:v libx264 -pix_fmt yuv420p -qp 0 -preset fast video.mp4".format(duration)

# Execute the command
subprocess.run(cmd, shell=True)

# Wait for the duration of the video
time.sleep(duration)
