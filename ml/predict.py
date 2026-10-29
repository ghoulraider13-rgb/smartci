#!/usr/bin/env python3
"""
Predict build failure probability for current commit.
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import json

from features import get_current_diff_features, prepare_features


def main():
    model_path = Path('ml/model.joblib')
    feature_cols_path = Path('ml/feature_cols.json')

    if not model_path.exists():
        print("Model not found. Run training first.")
        return

    if not feature_cols_path.exists():
        print("Feature columns not found. Run training first.")
        return

    # Load model and feature columns
    model = joblib.load(model_path)
    with open(feature_cols_path) as f:
        feature_cols = json.load(f)

    # Get current diff features
    features = get_current_diff_features()

    # Add engineered features
    features['total_lines'] = features['lines_added'] + features['lines_deleted']
    features['is_pricing'] = 1 if features['module'] == 'pricing' else 0
    features['is_cart'] = 1 if features['module'] == 'cart' else 0
    features['is_inventory'] = 1 if features['module'] == 'inventory' else 0
    features['hour'] = pd.Timestamp.now().hour
    features['day_of_week'] = pd.Timestamp.now().dayofweek

    # Create feature vector
    X = pd.DataFrame([features])
    X = X[feature_cols].fillna(0)

    # Predict
    proba = model.predict_proba(X)[0, 1]  # Probability of failure (class 1)
    pred = model.predict(X)[0]

    # Output
    print(f"Build Failure Prediction")
    print(f"=========================")
    print(f"Failure probability: {proba:.2%}")
    print(f"Prediction: {'FAIL' if pred == 1 else 'PASS'}")
    print(f"Features: {features}")

    # GitHub Actions output
    import os
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"failure_probability={proba:.4f}\n")
            f.write(f"prediction={'fail' if pred == 1 else 'pass'}\n")

    # Also write to step summary
    github_summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if github_summary:
        with open(github_summary, 'a') as f:
            f.write(f"## Build Failure Prediction\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Failure Probability | {proba:.2%} |\n")
            f.write(f"| Prediction | {'FAIL' if pred == 1 else 'PASS'} |\n")
            f.write(f"\n*Warning only - does not block the build*\n")


if __name__ == '__main__':
    main()