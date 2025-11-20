import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
import argparse

def train_supervised(df, label_col="label", model_out="models/supervised_rf.pkl"):
    # Generate heuristic labels if not present
    if label_col not in df.columns:
        print("[INFO] Generating heuristic labels from vpn_like_ip_ratio...")
        df[label_col] = df['vpn_like_ip_ratio'].apply(lambda x: 1 if x > 0.5 else 0)

    # Encode label if it is string (e.g. "VPN", "Non-VPN")
    if df[label_col].dtype == 'object':
        print(f"[INFO] Encoding string labels in '{label_col}' column...")
        # Map "VPN" -> 1, everything else -> 0
        df[label_col] = df[label_col].apply(lambda x: 1 if str(x).strip().lower() == 'vpn' else 0)

    # Features (exclude non-numeric columns)
    # Ensure we don't try to drop label_col if it wasn't selected by select_dtypes
    numeric_df = df.select_dtypes(include=['float64','int64'])
    if label_col in numeric_df.columns:
        X = numeric_df.drop(columns=[label_col])
    else:
        X = numeric_df
        
    y = df[label_col]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Random Forest Classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Predictions and evaluation
    y_pred = clf.predict(X_test)
    print("=== Supervised Model ===")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save model
    Path(model_out).parent.mkdir(exist_ok=True, parents=True)
    joblib.dump(clf, model_out)
    print(f"[OK] Supervised model saved at {model_out}")
    return clf

def train_unsupervised(df, model_out="models/unsupervised_if.pkl"):
    # Use all numeric features for anomaly detection
    X = df.select_dtypes(include=['float64','int64']).copy()

    # Isolation Forest (unsupervised)
    iso = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    iso.fit(X)

    # Predict anomaly scores
    df['vpn_anomaly_score'] = iso.decision_function(X)  # higher = more normal
    df['vpn_anomaly_label'] = iso.predict(X)            # -1 = anomaly, 1 = normal

    # Save model
    Path(model_out).parent.mkdir(exist_ok=True, parents=True)
    joblib.dump(iso, model_out)
    print(f"[OK] Unsupervised model saved at {model_out}")

    print("=== Unsupervised Model ===")
    print(f"Number of anomalies detected: {(df['vpn_anomaly_label'] == -1).sum()}")
    return iso, df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Supervised & Unsupervised VPN Models")
    parser.add_argument("--csv", required=True, help="Input ML-ready CSV file")
    parser.add_argument("--supervised_out", default="models/supervised_rf.pkl", help="Output path for supervised model")
    parser.add_argument("--unsupervised_out", default="models/unsupervised_if.pkl", help="Output path for unsupervised model")
    args = parser.parse_args()

    # Load data
    df = pd.read_csv(args.csv)

    # Train supervised model
    train_supervised(df, model_out=args.supervised_out)

    # Train unsupervised model
    train_unsupervised(df, model_out=args.unsupervised_out)
