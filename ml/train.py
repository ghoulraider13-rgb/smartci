#!/usr/bin/env python3
"""
Train build failure prediction model.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler

from features import load_data, prepare_features


def train_models(X_train, y_train, X_test, y_test, feature_cols):
    """Train and evaluate models."""
    models = {
        'logistic': LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
        'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
    }

    results = {}

    for name, model in models.items():
        print(f"\n{'='*50}")
        print(f"Training {name}...")
        print(f"{'='*50}")

        if name == 'logistic':
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_proba = model.predict_proba(X_test_scaled)[:, 1]
            results[name] = {'model': model, 'scaler': scaler}
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]
            results[name] = {'model': model, 'scaler': None}

        # Metrics
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, zero_division=0))

        print("Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)

        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary', zero_division=0)
        print(f"\nPrecision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1: {f1:.4f}")

        # Feature importance
        if name == 'logistic':
            importances = pd.DataFrame({
                'feature': feature_cols,
                'coefficient': model.coef_[0]
            }).sort_values('coefficient', key=abs, ascending=False)
        else:
            importances = pd.DataFrame({
                'feature': feature_cols,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)

        print(f"\nTop 10 Features:")
        print(importances.head(10).to_string(index=False))

        results[name]['importances'] = importances
        results[name]['predictions'] = y_pred
        results[name]['probabilities'] = y_proba

    return results


def naive_baseline(y_test):
    """Always predict pass (class 0)."""
    y_pred = np.zeros_like(y_test)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary', zero_division=0)
    print(f"\n{'='*50}")
    print("Naive Baseline (Always Predict Pass)")
    print(f"{'='*50}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1: {f1:.4f}")
    print(f"Accuracy: {(y_test == 0).mean():.4f}")


def main():
    real_path = Path('ml/data/real_runs.csv')
    generated_path = Path('ml/data/generated_runs.csv')

    df = load_data(real_path, generated_path)
    if df.empty:
        print("No data found")
        return

    X, y, feature_cols = prepare_features(df)

    # Temporal split (first 70% train, last 30% test)
    split_idx = int(len(df) * 0.7)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    print(f"Train class dist: {y_train.value_counts().to_dict()}")
    print(f"Test class dist: {y_test.value_counts().to_dict()}")

    # Naive baseline
    naive_baseline(y_test)

    # Train models
    results = train_models(X_train, y_train, X_test, y_test, feature_cols)

    # Save best model (random forest)
    best_model = results['random_forest']['model']
    model_path = Path('ml/model.joblib')
    joblib.dump(best_model, model_path)
    print(f"\nSaved best model to {model_path}")

    # Save feature columns for prediction
    import json
    with open(Path('ml/feature_cols.json'), 'w') as f:
        json.dump(feature_cols, f)

    # Save scaler for logistic regression
    joblib.dump(results['logistic']['scaler'], Path('ml/scaler.joblib'))

    # Print summary table
    print(f"\n{'='*50}")
    print("MODEL COMPARISON")
    print(f"{'='*50}")
    print(f"{'Model':<20} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print(f"{'-'*50}")

    for name in ['logistic', 'random_forest']:
        y_pred = results[name]['predictions']
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary', zero_division=0)
        print(f"{name:<20} {precision:>10.4f} {recall:>10.4f} {f1:>10.4f}")

    # Naive baseline
    y_pred_naive = np.zeros_like(y_test)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred_naive, average='binary', zero_division=0)
    print(f"{'naive (always pass)':<20} {precision:>10.4f} {recall:>10.4f} {f1:>10.4f}")


if __name__ == '__main__':
    main()