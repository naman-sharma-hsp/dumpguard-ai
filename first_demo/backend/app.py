from flask import Flask, Response, jsonify
import cv2
import time
import json
import os
from ultralytics import YOLO

# ======================================
# CONFIG
# ======================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VIDEOS = {
    "CCTV-01": os.path.join(BASE_DIR, "../videos/cam01.mp4"),
    "CCTV-02": os.path.join(BASE_DIR, "../videos/cam02.mp4")
}

SNAPSHOT_DIR = os.path.join(BASE_DIR, "../snapshots")
ALERT_JSON = os.path.join(BASE_DIR, "../data/alerts.json")

os.makedirs(SNAPSHOT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(ALERT_JSON), exist_ok=True)

model = YOLO("yolov8n.pt")
GARBAGE_CLASSES = ["backpack", "handbag", "bottle"]

# ======================================
# STATE CONSTANTS
# ======================================
IDLE = "IDLE"
OBSERVING = "OBSERVING"
SUSPECT = "SUSPECT"
CONFIRMED = "CONFIRMED"
COOLDOWN = "COOLDOWN"

SOFT_TIME = 0.5
HARD_TIME = 1.0
COOLDOWN_TIME = 2.0

# ======================================
# STATE PER CAMERA
# ======================================
camera_state = {}

alerts = []

if os.path.exists(ALERT_JSON):
    try:
        with open(ALERT_JSON, "r") as f:
            alerts = json.load(f)
            if not isinstance(alerts, list):
                alerts = []
    except (json.JSONDecodeError, ValueError):
        alerts = []

for cam in VIDEOS:
    camera_state[cam] = {
        "state": IDLE,
        "garbage_first_seen": None,
        "last_alert_time": -999
    }

# ======================================
# SAVE ALERT
# ======================================
def save_alert(cam, frame, boxes, video_sec):
    snapshot_name = f"{cam}_{int(video_sec)}.jpg"
    snapshot_path = os.path.join(SNAPSHOT_DIR, snapshot_name)
    cv2.imwrite(snapshot_path, frame)

    alert = {
        "camera": cam,
        "time": time.strftime("%H:%M:%S", time.gmtime(int(video_sec))),
        "video_second": round(video_sec, 2),
        "confidence": 0.95,
        "snapshot": f"snapshots/{snapshot_name}",
        "status": "ILLEGAL DUMPING DETECTED",
        "boxes": [
            {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "label": "garbage"}
            for (x1, y1, x2, y2) in boxes
        ]
    }

    alerts.append(alert)

    with open(ALERT_JSON, "w") as f:
        json.dump(alerts, f, indent=2)

# ======================================
# YOLO DETECTION
# ======================================
def yolo_detect(frame, video_sec):
    results = model(frame, conf=0.4, verbose=False)[0]

    persons, garbage = [], []

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if label == "person":
            persons.append((x1, y1, x2, y2))

        if label in GARBAGE_CLASSES:
            offset = int((video_sec % 3) * 4)
            garbage.append((x1 + offset, y1, x2 + offset, y2))

    return persons, garbage

# ======================================
# STATE MACHINE
# ======================================
def update_state(cam, frame, garbage, video_sec):
    s = camera_state[cam]

    # Cooldown window
    if video_sec - s["last_alert_time"] < COOLDOWN_TIME:
        s["state"] = COOLDOWN
        return

    if s["state"] == IDLE:
        if garbage:
            s["garbage_first_seen"] = video_sec
            s["state"] = OBSERVING

    elif s["state"] == OBSERVING:
        if not garbage:
            s["state"] = IDLE
        elif video_sec - s["garbage_first_seen"] >= SOFT_TIME:
            s["state"] = SUSPECT

    elif s["state"] == SUSPECT:
        if not garbage:
            s["state"] = IDLE
        elif video_sec - s["garbage_first_seen"] >= HARD_TIME:
            s["state"] = CONFIRMED

    elif s["state"] == CONFIRMED:
        save_alert(cam, frame, garbage, video_sec)
        s["last_alert_time"] = video_sec
        s["state"] = COOLDOWN

    elif s["state"] == COOLDOWN:
        if not garbage:
            s["state"] = IDLE

# ======================================
# VIDEO STREAM
# ======================================
def generate_stream(cam):
    cap = cv2.VideoCapture(VIDEOS[cam])

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            camera_state[cam]["state"] = IDLE
            camera_state[cam]["garbage_first_seen"] = None
            camera_state[cam]["last_alert_time"] = -999
            continue

        video_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

        persons, garbage = yolo_detect(frame, video_sec)
        update_state(cam, frame, garbage, video_sec)

        for (x1, y1, x2, y2) in persons:
            cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0), 2)

        for (x1, y1, x2, y2) in garbage:
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)

        cv2.putText(frame, f"{cam} | {camera_state[cam]['state']} | {video_sec:.2f}s",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

        _, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")

# ======================================
# FLASK
# ======================================
app = Flask(__name__)

@app.route("/video_feed_1")
def video_feed_1():
    return Response(generate_stream("CCTV-01"),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/video_feed_2")
def video_feed_2():
    return Response(generate_stream("CCTV-02"),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/alerts")
def get_alerts():
    return jsonify(alerts)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
