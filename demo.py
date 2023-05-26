import GPlayer
import time
import cv2

video_pipeline = f'v4l2src device=/dev/video0 ! video/x-raw, format=YUY2, width=640, height=480, framerate=30/1 ! nvvidconv ! video/x-raw(memory:NVMM) ! appsink'
cap_send = cv2.VideoCapture(video_pipeline, cv2.CAP_GSTREAMER)
w = cap_send.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap_send.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap_send.get(cv2.CAP_PROP_FPS)
out_send = cv2.VideoWriter('appsrc ! nvh264enc ! rtph264pay pt=96 config-interval=1 ! udpsink host=100.117.209.85 port=5201'\
         ,cv2.CAP_GSTREAMER\
         ,0\
         , 30\
         , (640, 480)\
         , True)
if not cap_send.isOpened() or not out_send.isOpened():
  print('VideoCapture or VideoWriter not opened')
  exit(0)

print('Src opened, %dx%d @ %d fps' % (w, h, fps))

while True:
  ret,frame = cap_send.read()
  if not ret:
    print('empty frame')
    break
  if out_send.isOpened():
    out_send.write(frame)
  if cv2.waitKey(1)&0xFF == ord('q'):
    break
cap_send.release()
out_send.release()
