import cv2
from ultralytics import YOLO
import time

# Khởi tạo mô hình YOLO (Dùng bản Nano - yolov8n.pt cho tốc độ nhanh nhất để test)
print("[INFO] Đang nạp mô hình YOLO...")
model = YOLO("yolo26n.pt") 

# Mở Webcam laptop (ID mặc định là 0)
print("[INFO] Đang kết nối luồng Video...")
cap = cv2.VideoCapture(0)

# Cấu hình độ phân giải cho khung hình (giả lập camera UAV)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("🔥 [HERETIC C] Hệ thống sẵn sàng! Bấm phím 'q' để thoát.")

# Tính FPS
prev_time = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("[LỖI] Không thể đọc dữ liệu từ Webcam.")
        break

    # 1. Đưa khung hình vào YOLO để nhận diện
    results = model(frame, stream=False)

    # 2. Lấy khung hình đã tự động vẽ Bounding Box
    annotated_frame = results[0].plot()

    # 3. Tính toán và Hiển thị FPS lên góc màn hình
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    cv2.putText(annotated_frame, f"FPS: {int(fps)}", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.putText(annotated_frame, "HERETIC HUD - Phase 1", (20, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

    # 4. Xuất luồng video ra màn hình
    cv2.imshow("Heretic HUD - Giao diện Nhận diện", annotated_frame)

    # Đợi phím 'q' để thoát vòng lặp
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[INFO] Đang đóng hệ thống...")
        break

# Dọn dẹp bộ nhớ
cap.release()
cv2.destroyAllWindows()