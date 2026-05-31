from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

img = cv2.imread("test.jpg")
results = model(img)

for result in results:
    for box in result.boxes:
        label = result.names[int(box.cls)]
        confidence = float(box.conf)
        print(f"Detected: {label} ({confidence:.0%} confidence)")
