import cv2
from pathlib import Path
from ultralytics import YOLO

model = YOLO('NEWFIRE.pt')
cap = cv2.VideoCapture("FIRE.mov")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Phát hiện
    results = model.track(frame, stream=True)
    for r in results:
        boxes = r.boxes.xyxy
        confs = r.boxes.conf
        cls_ids = r.boxes.cls
        for box, conf, cls in zip(boxes, confs, cls_ids):
            if conf > 0.4 :
                x1, y1, x2, y2 = map(int, box)
                label = f"{model.names[int(cls)]} {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 2)
                cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

    cv2.imshow("YOLO Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()