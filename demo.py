import GPlayer
import time
import cv2

def on_msg(topic, message):
  print('onMsg callback;')
  if topic == 'testcmd':
    print(f'{topic} : {message}')

gplayer = GPlayer.GPlayer()
gplayer.on_msg = on_msg

cap_send = cv2.VideoCapture('videotestsrc ! video/x-raw,framerate=20/1 ! videoscale ! videoconvert ! appsink drop=1', cv2.CAP_GSTREAMER)
#out_send = cv2.VideoWriter('gst-launch-1.0 appsrc ! videoconvert ! omxh264enc ! rtph264pay pt=96 config-interval=1 ! udpsink host=100.117.209.85 port=5200',cv2.CAP_GSTREAMER,0, 20, (320,240), True)
#if not cap_send.isOpened() or not out_send.isOpened():
#  print('VideoCapture or VideoWriter not opened')
#  exit(0)

while True:
  ret,frame = cap_send.read()
  if not ret:
    print('empty frame')
    break
    cv2.imshow('send', frame)
    #out_send.write(frame)
    if cv2.waitKey(1)&0xFF == ord('q'):
      break
cap_send.release()
#out_send.release()
