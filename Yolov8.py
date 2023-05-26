import os
import cv2
import warnings
from collections import namedtuple
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
from numpy import ndarray
import TRTEngine as TRTE

os.environ['CUDA_MODULE_LOADING'] = 'LAZY'
warnings.filterwarnings(action='ignore', category=DeprecationWarning)

def letterbox(im: ndarray,
              new_shape: Union[Tuple, List] = (640, 640),
              color: Union[Tuple, List] = (0, 0, 0)) \
        -> Tuple[ndarray, float, Tuple[float, float]]:
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[
        1]  # wh padding

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im,
                            top,
                            bottom,
                            left,
                            right,
                            cv2.BORDER_CONSTANT,
                            value=color)  # add border
    return im, r, (dw, dh)
def blob(im: ndarray, return_seg: bool = False) -> Union[ndarray, Tuple]:
    if return_seg:
        seg = im.astype(np.float32) / 255
    im = im.transpose([2, 0, 1])
    im = im[np.newaxis, ...]
    im = np.ascontiguousarray(im).astype(np.float32) / 255
    if return_seg:
        return im, seg
    else:
        return im
enggine = TRTE.TRTEngine('yolov8s.engine')
H, W = enggine.inp_info[0].shape[-2:]

def detect(image):

  bgr, ratio, dwdh = letterbox(image, (W, H))
  rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
  tensor = blob(rgb, return_seg=False)
  dwdh = np.array(dwdh * 2, dtype=np.float32)
  tensor = np.ascontiguousarray(tensor)
  results = enggine(tensor)
  print(results)

  bboxes, scores, labels = results
  bboxes -= dwdh
  bboxes /= ratio

  CLASSES = ('person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
             'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
             'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
             'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
             'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
             'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
             'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
             'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
             'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
             'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
             'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
             'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven',
             'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
             'scissors', 'teddy bear', 'hair drier', 'toothbrush')
  for (bbox, score, label) in zip(bboxes, scores, labels):
      bbox = bbox.round().astype(np.int32).tolist()
      cls_id = int(label)
      cls = CLASSES[cls_id]
      color = (0,255,0)
      cv2.rectangle(image, tuple(bbox[:2]), tuple(bbox[2:]), color, 2)
      cv2.putText(image,
                  f'{cls}:{score:.3f}', (bbox[0], bbox[1] - 2),
                  cv2.FONT_HERSHEY_SIMPLEX,
                  0.75, [225, 255, 255],
                  thickness=2)
  return image

video_pipeline = 'v4l2src device=/dev/vifwewedeo0 ! video/x-raw, format=YUY2, width=640, height=480, framerate=30/1! videoconvert ! video/x-raw,format=BGR ! appsink'
cap_send = cv2.VideoCapture(video_pipeline, cv2.CAP_GSTREAMER)
w = cap_send.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap_send.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap_send.get(cv2.CAP_PROP_FPS)
out_send = cv2.VideoWriter('appsrc !  nvvidconv ! nvv4l2h264enc ! omxh264enc ! rtph264pay pt=96 config-interval=1 ! udpsink host=127.0.0.1 port=5240'\
                           ,cv2.CAP_GSTREAMER\
                           ,0\
                           , fps\
                           , (int(w), int(h))\
                           , True)
if not cap_send.isOpened():
  print('VideoCapture not opened')
  exit(0)
if not out_send.isOpened():
  print('VideoWriter not opened')
  exit(0)

print('Src opened, %dx%d @ %d fps' % (w, h, fps))

while True:
  ret,frame = cap_send.read()
  if not ret:
    print('empty frame')
    break
  frame = detect(frame)
  if out_send.isOpened():
    out_send.write(frame)
  if cv2.waitKey(1)&0xFF == ord('q'):
    break
cap_send.release()
out_send.release()
