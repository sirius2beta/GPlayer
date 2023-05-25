import cv2
from ultralytics import YOLO
from ultralytics.yolo.utils.plotting import Annotator


model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)


if not cap.isOpened():
    print('cap not opened')
    exit(0)
while True:
    ret, frame = cap.read()
    if ret:
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model.predict(img, conf=0.5, classes=0)
        annotator = Annotator(img)

        for r in results:
            for box in r.boxes:
                b = box.xyxy[0]
                c = box.cls
                annotator.box_label(b, f"{r.names[int(c)]} {float(box.conf):.2}")

        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imshow("windows", img)
        key = cv2.waitKey(1)
        if key == 27:
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()
