import cv2
import time
import math
import json
from ultralytics import YOLO

# Khởi tạo mô hình
print("[INFO] Đang nạp mô hình YOLO26...")
model = YOLO("yolo26n.pt") # Chạy tạm CPU, tối ưu GPU sau

cap = cv2.VideoCapture(0)
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# Tọa độ tâm khung hình (Giả định là vị trí Người lính)
CENTER_X = FRAME_WIDTH // 2
CENTER_Y = FRAME_HEIGHT // 2

# Hệ số quy đổi giả lập: 1 pixel = 0.05 mét 
PIXEL_TO_METER = 0.05 

# Giả lập GPS của người lính tại Quyết Thắng, Thái Nguyên
SOLDIER_GPS = {"lat": 21.0333, "lon": 105.7333, "location": "Tu Liem, Ha Noi"}

def calculate_tactical_telemetry(box, center_x, center_y, scale):
    """Tính toán khoảng cách và hướng từ tâm (Người lính) đến Mục tiêu"""
    # Tâm của mục tiêu
    x1, y1, x2, y2 = box.xyxy[0].tolist()
    obj_x = (x1 + x2) / 2
    obj_y = (y1 + y2) / 2

    # Tính độ lệch tọa độ (dx, dy)
    dx = obj_x - center_x
    dy = center_y - obj_y  # Trục Y trong ảnh ngược với trục Y toán học

    # Tính khoảng cách (mét)
    distance = math.sqrt(dx**2 + dy**2) * scale

    # Tính góc phương vị (Bearing) - Dùng Atan2
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    
    # Quy đổi góc ra hướng la bàn
    if -45 <= angle_deg <= 45: direction = "Đông"
    elif 45 < angle_deg < 135: direction = "Bắc"
    elif 135 <= angle_deg <= 180 or -180 <= angle_deg <= -135: direction = "Tây"
    else: direction = "Nam"

    return round(distance, 1), direction

print("🔥 [HERETIC C - PHASE 2] Bắt đầu tính toán không gian! Bấm 'q' để thoát.")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Vẽ vị trí Người lính (Tâm màn hình) bằng dấu cộng màu đỏ
    cv2.drawMarker(frame, (CENTER_X, CENTER_Y), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)
    cv2.putText(frame, "Soldier Pos", (CENTER_X + 10, CENTER_Y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Chạy YOLO
    results = model(frame, stream=False, verbose=False)
    
    tactical_data = []

    # Xử lý các đối tượng phát hiện được
    for r in results:
        boxes = r.boxes
        for box in boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            
            # Tính khoảng cách và hướng
            distance, direction = calculate_tactical_telemetry(box, CENTER_X, CENTER_Y, PIXEL_TO_METER)
            
            # Đóng gói vào List Dictionary
            tactical_data.append({
                "target": class_name,
                "distance_m": distance,
                "bearing": direction
            })

            # Vẽ thông tin lên khung hình (HUD)
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{class_name} | {distance}m {direction}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Hiển thị Json ra Terminal nếu có mục tiêu
    if tactical_data:
        json_payload = {
            "soldier_gps": SOLDIER_GPS,
            "detected_threats": tactical_data
        }
        print(json.dumps(json_payload, ensure_ascii=False, indent=2))

    # Hiển thị HUD
    cv2.imshow("Heretic HUD - Phase 2 (Radar Mode)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()