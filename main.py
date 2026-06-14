from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

GRIP_MAP = {
    "bottle": "power",
    "vase": "power",
    "cup": "palmar",
    "fork": "lateral",
    "knife": "lateral",
    "spoon": "lateral",
    "cell phone": "flat",
    "book": "flat",
    "scissors": "power",
    "remote": "flat",
    "toothbrush": "pinch",
    "pen": "pinch",
}

CONFIDENCE_THRESHOLD = 0.60

# 0 means use the first available camera (your laptop webcam)
cap = cv2.VideoCapture(0)

while True:
    # Read one frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Camera not found")
        break

    results = model(frame)

    for result in results:
        for box in result.boxes:
            label = result.names[int(box.cls)]
            confidence = float(box.conf)

            if confidence >= CONFIDENCE_THRESHOLD:
                grip = GRIP_MAP.get(label, None)
                if grip:
                    print(f"Detected: {label} ({confidence:.0%}) → {grip} grip")

    # Show the camera feed in a window
    cv2.imshow("Prosthetic Camera Feed", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
