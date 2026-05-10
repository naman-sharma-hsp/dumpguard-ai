# DumpGuard AI 🗑️🤖  
### Smart Waste Management & Illegal Dumping Prediction System

DumpGuard AI is an AI-powered web platform designed to predict, visualize, and demonstrate illegal waste dumping risks in urban areas. The system combines machine learning, data analytics, and interactive dashboards to support smarter city waste management.

---

## 🚀 Project Overview

Illegal dumping is a major urban challenge causing environmental damage, public health risks, and high cleanup costs. DumpGuard AI addresses this by shifting from reactive cleanup to **predictive prevention** using AI.

The project:
- Predicts dumping risk levels using machine learning
- Displays AI-generated hotspots on an interactive map
- Analyzes complaint trends using charts
- Demonstrates AI monitoring through simulated CCTV footage

---

## 🧠 Core Features

### 1️⃣ AI Risk Prediction Model
- Trained using historical and logical urban data
- Uses Random Forest Classifier
- Input features:
  - Complaint count
  - Nearby empty plots
  - Nearby markets
  - Rainfall level
- Output:
  - Low / Medium / High risk classification

---

### 2️⃣ Live Monitoring Dashboard (Main Website)

#### 🗺️ Predictive Hotspot Map
- Interactive Leaflet.js map
- Color-coded risk zones:
  - 🔴 High Risk
  - 🟠 Medium Risk
  - 🟢 Low Risk
- Map updates using AI-predicted data
- Dynamic complaint bar chart (Chart.js)

#### 📹 CCTV Simulation (Demo)
- Simulated CCTV footage
- Demonstrates how AI-based detection could work
- Visual alerts for detected dumping activity

---

## 🏗️ Project Structure

WEBSITE/
├── second_demo/
│ ├── data/
│ │ ├── train_illegal_dumping_logical.csv
│ │ ├── predict_illegal_dumping_logical.csv
│ │ └── predicted_results.csv
│ ├── model/
│ │ ├── train_model.py
│ │ └── risk_predictor.py
│ ├── backend/
│ │ └── app.py
|
├── first_demo/
| ├── videos/
| │   ├── cam01.mp4
| │   └── cam02.mp4
| ├── snapshots/
| │   └── (auto-generated images)
| ├── model/
| │   └── detect_dumping.py
| ├── data/
| │   └── alerts.json
| ├── backend/
| │   └── app.py
| └── README.md
│
├── assets/
│ └── images/ # reference images
│
├── css/
│ └── style.css # main website styling
│
├── js/
│ ├── dashboard.js # map + chart logic
│ └── script.js
│
└── index.html # main website


🧠 Level 1 — Event memory

Save repeated dumping locations:

hotspots.json

🧠 Level 2 — Risk scoring

Camera risk increases over time

🧠 Level 3 — ML feedback loop

Snapshots → retrain model weekly

🧠 Level 4 — Live backend

Flask/FastAPI + WebSocket alerts