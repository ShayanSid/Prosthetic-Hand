from ultralytics import YOLO
import cv2

# Load the YOLOv8n Nano model (downloads automatically on first run)
model = YOLO("yolov8n.pt")

# Maps YOLO object labels to prosthetic grip types
# Note: some objects get unexpected labels (e.g, bottlles detected as
# vases)
# so both are mapped to the same grip
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

# Minimum confidence required before acting on a dection
CONFIDENCE_THRESHOLD = 0.60

def recommend_grip(image_path):
    img = cv2.imread(image_path)
    results = model(img)

    for result in results:
        for box in result.boxes:
            label = result.names[int(box.cls)]
            confidence = float(box.conf)

            if confidence >= CONFIDENCE_THRESHOLD:
                grip = GRIP_MAP.get(label, None)
                if grip:
                    print(f"Detected: {label} ({confidence:.0%} confidence)")
                    print(f"Recommended grip: {grip}")
                    return
                    
    print("No confident detection — try repositioning the object")

recommend_grip("test.jpg")
