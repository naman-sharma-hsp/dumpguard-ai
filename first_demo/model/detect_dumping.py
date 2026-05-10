import cv2
import json
import time
import os

# =========================
# CONFIG
# =========================
VIDEO_PATHS = {
    "CCTV-01": "../videos/cam01.mp4",
    "CCTV-02": "../videos/cam02.mp4"
}

ALERTS_PATH = "../data/alerts.json"
SNAPSHOT_DIR = "../snapshots"

CONF_THRESHOLD = 0.6

SOFT_TIME = 0.1     # seconds
HARD_TIME = 2       # seconds
COOLDOWN_TIME = 3   # seconds

# =========================
# STATES
# =========================
STATE_IDLE = "IDLE"
STATE_OBSERVING = "OBSERVING"
STATE_SUSPECT = "SUSPECT"
STATE_CONFIRMED = "CONFIRMED"
STATE_COOLDOWN = "COOLDOWN"

# =========================
# HOTSPOTS (REALISM)
# =========================
HOTSPOTS = {
    "CCTV-01": [(100, 100, 1900, 1700)],
    "CCTV-02": [(1200, 1600, 700, 2100)]
}

# =========================
# SETUP
# =========================
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

alerts = []

def in_hotspot(cam, box):
    if cam not in HOTSPOTS:
        return False
    x1, y1, x2, y2 = box
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    for hx1, hy1, hx2, hy2 in HOTSPOTS[cam]:
        if hx1 <= cx <= hx2 and hy1 <= cy <= hy2:
            return True
    return False

# =========================
# PER CAMERA STATE
# =========================
camera_state = {}

for cam in VIDEO_PATHS:
    camera_state[cam] = {
        "state": STATE_IDLE,
        "state_start": 0,
        "last_alert": -999,
        "interaction": False,
        "dumping_logged": False
    }

# =========================
# MAIN LOOP
# =========================
for cam_id, video_path in VIDEO_PATHS.items():

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_no = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_no += 1
        current_sec = frame_no / fps

        state_data = camera_state[cam_id]
        state = state_data["state"]

        # -------------------------
        # FAKE DETECTION (SIMULATION)
        # -------------------------
        garbage_boxes = []
        person_boxes = []

        # simulate detection windows
        if 0 < current_sec < 40:
            garbage_boxes.append((300, 350, 450, 550))
        if 0 < current_sec < 40:
            person_boxes.append((280, 300, 360, 500))

        garbage_detected = len(garbage_boxes) > 0
        person_detected = len(person_boxes) > 0

        # -------------------------
        # COOLDOWN CHECK
        # -------------------------
        if current_sec - state_data["last_alert"] < COOLDOWN_TIME:
            state_data["state"] = STATE_COOLDOWN
            continue

        # -------------------------
        # STATE MACHINE
        # -------------------------
        if garbage_detected:
            if state == STATE_IDLE:
                state_data["state"] = STATE_OBSERVING
                state_data["state_start"] = current_sec
                state_data["interaction"] = False

            if person_detected:
                state_data["interaction"] = True

            elapsed = current_sec - state_data["state_start"]

            if elapsed >= SOFT_TIME:
                state_data["state"] = STATE_SUSPECT

            if elapsed >= HARD_TIME:
                state_data["state"] = STATE_CONFIRMED

        else:
            state_data["state"] = STATE_IDLE

        # -------------------------
        # CONFIDENCE CALCULATION
        # -------------------------
        if (
            state_data["state"] == STATE_CONFIRMED
            and not state_data["dumping_logged"]
        ):
            state_data["dumping_logged"] = True
            state_data["last_alert"] = current_sec
            state_data["state"] = STATE_COOLDOWN
            confidence = 0.4
            reasons = ["Garbage detected"]

            if state_data["interaction"]:
                confidence += 0.2
                reasons.append("Human interaction detected")

            confidence += 0.25
            reasons.append("Object unattended for long duration")

            for g in garbage_boxes:
                if in_hotspot(cam_id, g):
                    confidence += 0.1
                    reasons.append("Dumping hotspot zone")
                    break

            confidence = min(confidence, 0.99)

            if confidence >= CONF_THRESHOLD:
                snapshot_name = f"{cam_id}_{int(current_sec)}.jpg"
                snapshot_path = os.path.join(SNAPSHOT_DIR, snapshot_name)
                cv2.imwrite(snapshot_path, frame)

                alerts.append({
                    "camera": cam_id,
                    "time": time.strftime("%H:%M:%S", time.gmtime(int(current_sec))),
                    "video_second": int(current_sec),
                    "confidence": round(confidence, 2),
                    "snapshot": f"snapshots/{snapshot_name}",
                    "status": "ILLEGAL DUMPING CONFIRMED",
                    "alert_type": "HARD",
                    "reason": reasons,
                    "boxes": [
                        {
                            "x1": g[0],
                            "y1": g[1],
                            "x2": g[2],
                            "y2": g[3],
                            "label": "garbage"
                        } for g in garbage_boxes
                    ]
                })

                state_data["last_alert"] = current_sec
                state_data["state"] = STATE_COOLDOWN

    cap.release()

# =========================
# SAVE ALERTS
# =========================
with open(ALERTS_PATH, "w") as f:
    json.dump(alerts, f, indent=2)

print("Detection completed. Alerts saved.")
