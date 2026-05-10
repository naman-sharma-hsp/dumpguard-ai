// ---------------- CONFIG ----------------
const snapshotBuffer = [];   // holds max 4 snapshots

const ALERT_JSON = "first_demo/data/alerts.json";
let snapshotsLocked = true;

let alertsData = [];

// ---------------- HELPERS ----------------
function timeToSeconds(timeStr) {
  // "00:00:20" → 20
  const parts = timeStr.split(":").map(Number);
  return parts[0] * 3600 + parts[1] * 60 + parts[2];
}

// ---------------- DRAW BOXES ----------------
function drawBoxes(video, canvas, boxes) {
  if (!video || !canvas) return;

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.lineWidth = 3;
  ctx.font = "14px Arial";
  ctx.strokeStyle = "red";
  ctx.fillStyle = "red";

  boxes.forEach(box => {
    if (box.label !== "garbage") return;

    const x = box.x1;
    const y = box.y1;
    const w = box.x2 - box.x1;
    const h = box.y2 - box.y1;

    ctx.strokeRect(x, y, w, h);
    ctx.fillText("GARBAGE", x + 4, y - 6);
  });
}

// ---------------- ALERT PANEL ----------------
function showAlert(alert) {
  const container = document.getElementById("video-alerts");

  let snapshotPath = alert.snapshot.replace("\\", "/");
  if (!snapshotPath.startsWith("first_demo/")) {
    snapshotPath = "first_demo/" + snapshotPath;
  }

  // ⛔ Prevent duplicate snapshots
  if (snapshotBuffer.some(s => s.path === snapshotPath)) return;

  snapshotBuffer.push({
    path: snapshotPath,
    camera: alert.camera,
    time: alert.time,
    confidence: alert.confidence
  });

  // 🔄 Remove oldest if more than 4
  if (snapshotBuffer.length > 4) {
    snapshotBuffer.shift();
  }

  renderSnapshots();
}




// ---------------- SYNC WITH VIDEO ----------------
function attachVideoSync(videoId, canvasId, cameraName) {
  const video = document.getElementById(videoId);
  const canvas = document.getElementById(canvasId);
  const ctx = canvas.getContext("2d");

  const camAlerts = alertsData.filter(a => a.camera === cameraName);

  const VISIBLE_DURATION = 3; // seconds boxes stay visible

  video.addEventListener("timeupdate", () => {
    const current = video.currentTime;

    let boxDrawn = false;

    camAlerts.forEach(alert => {
      const alertTime = timeToSeconds(alert.time);

      // SHOW window
      if (current >= alertTime && current <= alertTime + VISIBLE_DURATION) {
        showAlert(alert);
        drawBoxes(video, canvas, alert.boxes);
        boxDrawn = true;
      }
    });

    // If no alert should be visible → clear boxes + alert panel
    if (!boxDrawn) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      clearAlerts();
    }
  });

  // Reset on loop / restart
  video.addEventListener("ended", () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    clearAlerts();
  });

  video.addEventListener("seeked", () => {
    if (video.currentTime < 0.5) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      clearAlerts();
    }
  });

  video.addEventListener("ended", () => {
  snapshotBuffer.length = 0;

  //document.getElementById("video-alerts").innerHTML =
    //`<p class="no-alert">No illegal dumping detected yet</p>`;
});


}


// ---------------- LOAD ALERTS ----------------
async function init() {
  const res = await fetch(ALERT_JSON);
  alertsData = await res.json();

  attachVideoSync("video1", "canvas1", "CCTV-01");
  attachVideoSync("video2", "canvas2", "CCTV-02");

  const video = document.getElementById("video1");
  const alertsDiv = document.getElementById("video-alerts");

  video.addEventListener("ended", () => {
    snapshotBuffer.length = 0;
    alertsDiv.innerHTML = "";
    video.currentTime = 0;
    video.play();
  });

  const video2 = document.getElementById("video2"); 

  video2.addEventListener("ended", () => {
    snapshotBuffer.length = 0;
    alertsDiv.innerHTML = "";
    video2.currentTime = 0;
    video2.play();
  });
}

init();

function renderSnapshots() {
  const container = document.getElementById("video-alerts");
  container.innerHTML = "";

  snapshotBuffer.forEach(snap => {
    const div = document.createElement("div");
    div.className = "alert";

    div.innerHTML = `
      <strong>${snap.camera}</strong><br>
      ⏱ ${snap.time}<br>
      📊 ${(snap.confidence * 100).toFixed(1)}%
      <img src="${snap.path}" />
    `;

    container.appendChild(div);
  });
}

