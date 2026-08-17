from ultralytics import YOLO
from picamera2 import Picamera2
import time
import cv2
import numpy as np

# Load the YOLOv8 Nano model
model = YOLO("yolov8n.pt")

# Maps YOLO object labels to prosthetic grip types
# Note: some objects get unexpected labels (e.g. bottles detected as vases)
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

# Minimum confidence required before acting on a detection
CONFIDENCE_THRESHOLD = 0.60

# Set up Pi Camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

print("Camera started — point at an object")

while True:
    # Grab frame from Pi Camera
    start = time.time()
    frame = picam2.capture_array()

    results = model(frame, verbose=False)

    for result in results:
        for box in result.boxes:
            label = result.names[int(box.cls)]
            confidence = float(box.conf)
            print(f"Saw: {label} ({confidence:.0%})")


            if confidence >= CONFIDENCE_THRESHOLD:
                grip = GRIP_MAP.get(label, None)
                if grip:
                    print(f"Detected: {label} ({confidence:.0%}) → {grip} grip")

    print(f"Frame time: {(time.time()-start)*1000:.0f}ms")
picam2.stop()
