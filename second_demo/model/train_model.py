import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
data = pd.read_csv(r"E:\A.I\dumpguard-ai\WEBSITE\second_demo\data\train_illegal_dumping_logical.csv")

# Features and target
X = data[["complaint_count", "near_empty_plot", "near_market", "rainfall_mm"]]
y = data["risk_level"]

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save trained model
with open("dumpguard_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved successfully")
