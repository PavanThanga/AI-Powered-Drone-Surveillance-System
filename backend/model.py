from ultralytics import YOLO
import cv2
import torch

# Load model once (important for performance)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
model = YOLO("yolov8n.pt")
model_weapon=YOLO("C:\\Users\\PAVAN\\OneDrive\\Desktop\\AI Drone\\best.pt")

model.to(device)
model_weapon.to(device)

HUMAN_CLASSES = ["person"]
VEHICLE_CLASSES = ["car", "bus", "truck", "motorcycle", "bicycle"]


def process_video(input_path, output_path, human=True, vehicle=True, weapon=False):
    cap = cv2.VideoCapture(input_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps==0:
        fps=25

    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    out = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )

    human_detected = False
    vehicle_detected = False
    weapon_detected = False

    # Simple tracker: Run AI every N frames, and hold boxes for intermediates to speed up process
    frame_skip = 3
    frame_count = 0
    cached_boxes = []

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_skip == 0:
                cached_boxes = [] # clear cache
                
                results = model(frame, verbose=False)[0]

                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    if human and label in HUMAN_CLASSES:
                        human_detected = True
                        cached_boxes.append((x1, y1, x2, y2, (0, 255, 0)))

                    if vehicle and label in VEHICLE_CLASSES:
                        vehicle_detected = True
                        cached_boxes.append((x1, y1, x2, y2, (255, 0, 0)))

                # 🔴 2️⃣ Run weapon model separately
                if weapon:
                    results_weapon = model_weapon(frame, verbose=False)[0]

                    for box in results_weapon.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        weapon_detected = True
                        cached_boxes.append((x1, y1, x2, y2, (0, 0, 255)))
                        
            # Draw from cache
            for x1, y1, x2, y2, color in cached_boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

            out.write(frame)
            frame_count += 1
            
    finally:
        cap.release()
        out.release()

    return {
        "human": human_detected if human else False,
        "vehicle": vehicle_detected if vehicle else False,
        "weapon": weapon_detected if weapon else False  # placeholder
    }

def process_live_frame(frame, human=True, vehicle=True, weapon=False):
    results = model(frame, verbose=False)[0]


    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if human and label in HUMAN_CLASSES:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)


        if vehicle and label in VEHICLE_CLASSES:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)

    if weapon:
        results_weapon = model_weapon(frame, verbose=False)[0]

        for box in results_weapon.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 3) 

    return frame