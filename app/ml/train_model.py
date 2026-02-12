import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 1. GENERATE SYNTHETIC DATA
# We pretend we have data from 1,000 past deployments
np.random.seed(42)
n_samples = 1000

data = {
    # Feature 1: How many files changed? (More files = Higher Risk)
    "num_files": np.random.randint(1, 50, n_samples),
    
    # Feature 2: Is there a database migration? (1=Yes, 0=No)
    "has_migration": np.random.randint(0, 2, n_samples),
    
    # Feature 3: Did they delete code? (Lines deleted)
    "lines_deleted": np.random.randint(0, 100, n_samples),
    
    # Feature 4: Is it a Friday? (DevOps joke: deploying on Friday is risky)
    "is_friday": np.random.randint(0, 2, n_samples)
}

df = pd.DataFrame(data)

# 2. DEFINE THE "REALITY" (The Target Label)
# We create a formula for risk. In real life, this comes from incident reports.
# Formula: Big changes + Migrations + Friday = BOOM (1)
risk_probability = (
    (df["num_files"] * 0.02) + 
    (df["has_migration"] * 0.3) + 
    (df["is_friday"] * 0.2) +
    np.random.normal(0, 0.1, n_samples) # Add some noise/luck
)

# Convert probability to 0 (Safe) or 1 (Failed)
df["deployment_failed"] = (risk_probability > 0.5).astype(int)

print(f"Generated {n_samples} deployment records.")
print(df.head())

# 3. TRAIN THE MODEL
X = df.drop("deployment_failed", axis=1)
y = df["deployment_failed"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LogisticRegression()
model.fit(X_train, y_train)

# 4. EVALUATE
predictions = model.predict(X_test)
print(f"Model Accuracy: {accuracy_score(y_test, predictions):.2f}")

# 5. SAVE THE BRAIN
# We save the model to a file so the Worker can load it later.
joblib.dump(model, "app/ml/risk_model.pkl")
print("Model saved to app/ml/risk_model.pkl")