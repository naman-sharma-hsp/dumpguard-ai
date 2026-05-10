import pickle
import pandas as pd
import os

# Load trained model
model = pickle.load(open("dumpguard_model.pkl", "rb"))

# CSV to predict (change this file as needed)
predict_csv = os.path.join(os.path.dirname(__file__), "../data/predict_illegal_dumping_logical.csv")

# Load prediction CSV
data = pd.read_csv(predict_csv)

# Extract features
X = data[["complaint_count", "near_empty_plot", "near_market", "rainfall_mm"]]

# Predict risk
predictions = model.predict(X)

# Add predictions to DataFrame
data["risk_level"] = predictions

# Print results
print("Predicted Risk Levels:")
print(data[["area_id", "risk_level", "latitude", "longitude"]])

# Save results to a new CSV (optional)
data.to_csv(os.path.join(os.path.dirname(__file__), "../data/predicted_results.csv"), index=False)
