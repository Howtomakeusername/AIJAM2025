import cv2
import time
import requests
from ultralytics import YOLO

# Cấu hình ThingSpeak
THINGSPEAK_WRITE_KEY = "WKD8R1UG3JG6LS53"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

def send_to_thingspeak(value):
    """
    Gửi giá trị lên ThingSpeak.
    field1 sẽ nhận giá trị 'value'.
    """
    payload = {
        'api_key': THINGSPEAK_WRITE_KEY,
        'field4': value
    }
    try:
        r = requests.get(THINGSPEAK_URL, data=payload, timeout=5)
        if r.status_code == 200:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Gửi lên ThingSpeak thành công: {value}")
        else:
            print(f"[Error] ThingSpeak trả về mã {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[Error] Không thể kết nối ThingSpeak: {e}")

# Khởi tạo model và camera
model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(1)  # Chỉnh index tương ứng camera của bạn

# Các biến hỗ trợ đỡ gửi liên tục quá nhanh
person_last_sent = False
cooldown = 10  # giãn cách tối thiểu giữa hai lần gửi (giây)
last_send_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Không đọc được frame từ camera!")
        break

    frame = cv2.resize(frame, (640, 480))

    # Phát hiện
    results = model(frame, stream=True)
    person_detected = False

    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy()
        confs = r.boxes.conf.cpu().numpy()
        cls_ids = r.boxes.cls.cpu().numpy()
        for box, conf, cls in zip(boxes, confs, cls_ids):
            if model.names[int(cls)] != 'person':
                continue
            # Nếu đến đây, đã phát hiện person
            person_detected = True
            x1, y1, x2, y2 = map(int, box)
            label = f"person {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

    # Nếu phát hiện người và đang không trong trạng thái cooldown
    now = time.time()
    if person_detected and (not person_last_sent or now - last_send_time > cooldown):
        send_to_thingspeak(1)      # gửi giá trị 1 cho field1
        person_last_sent = True
        last_send_time = now
    elif not person_detected:
        if not person_detected and ( now - last_send_time > cooldown):
            send_to_thingspeak(0)  # gửi giá trị 0 cho field4
            last_send_time = now
        # reset flag để sẵn sàng phát hiện lần sau
        person_last_sent = False

    # Hiển thị khung hình
    cv2.imshow("YOLO Person Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
