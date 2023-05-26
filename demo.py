import GPlayer
import time
import cv2

video_pipeline = 'videotestsrc ! video/x-raw, format=BGR ! videoconvert ! appsink'
cap_send = cv2.VideoCapture(video_pipeline, cv2.CAP_GSTREAMER)
w = cap_send.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap_send.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap_send.get(cv2.CAP_PROP_FPS)
out_send = cv2.VideoWriter('appsrc ! jpegenc quality=80 ! rtpjpegpay ! udpsink host=192.168.0.2 port=5201'\
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
