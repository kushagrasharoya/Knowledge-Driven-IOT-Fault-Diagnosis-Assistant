"""
train_ai4i.py
-------------
Trains the Gradient Boosting model on the AI4I 2020 Predictive Maintenance dataset.
Saves the trained model, feature list, and chosen threshold (0.40) to models/fault_model.pkl.
"""

import os
import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

# 1. Load dataset
CSV_PATH = "ai4i2020.csv"
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"{CSV_PATH} not found. Please ensure the dataset is present.")

df = pd.read_csv(CSV_PATH)
print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

# 2. One-hot encode 'Type' ('L', 'M', 'H')
df_encoded = pd.get_dummies(df, columns=["Type"], prefix="Type", dtype=float)

# Ensure one-hot encoded columns exist
for col in ["Type_H", "Type_L", "Type_M"]:
    if col not in df_encoded.columns:
        df_encoded[col] = 0.0

# 3. Define feature columns and target
FEATURES = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "Type_H",
    "Type_L",
    "Type_M"
]

TARGET = "Machine failure"

X = df_encoded[FEATURES]
y = df_encoded[TARGET]

print(f"Features ({len(FEATURES)}): {FEATURES}")
print(f"Class distribution: {dict(y.value_counts())}")

# 4. Train/test split (80/20 stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. Train Gradient Boosting Classifier
print("\nTraining Gradient Boosting Classifier...")
model = GradientBoostingClassifier(random_state=42)
model.fit(X_train, y_train)

# 6. Evaluate with threshold 0.40
y_proba = model.predict_proba(X_test)[:, 1]
threshold = 0.40
y_pred = (y_proba >= threshold).astype(int)

auc = roc_auc_score(y_test, y_proba)
cm = confusion_matrix(y_test, y_pred)

print(f"\n--- Evaluation Results (Threshold: {threshold}) ---")
print(f"ROC-AUC Score: {auc:.4f}")
print("Confusion Matrix:")
print(cm)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, digits=4))

# 7. Save model package
os.makedirs("models", exist_ok=True)
model_pkg = {
    "model": model,
    "features": FEATURES,
    "threshold": threshold
}

joblib.dump(model_pkg, "models/fault_model.pkl")
print("✅ Saved fault model package to models/fault_model.pkl")
