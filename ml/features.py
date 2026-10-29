#!/usr/bin/env python3
"""
Feature extraction for build failure prediction.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict
import subprocess
import json


def get_current_diff_features() -> Dict:
    """Extract features from current git diff (for prediction)."""
    try:
        # Get diff stats
        result = subprocess.run(
            ['git', 'diff', '--stat', 'HEAD~1'],
            capture_output=True, text=True
        )
        output = result.stdout.strip()

        files_changed = 0
        lines_added = 0
        lines_deleted = 0

        for line in output.split('\n'):
            if 'file' in line and 'changed' in line:
                parts = line.split(',')
                if len(parts) >= 3:
                    files_changed = int(parts[0].strip().split()[0])
                    lines_added = int(parts[1].strip().split()[0])
                    lines_deleted = int(parts[2].strip().split()[0])

        # Get changed file names
        result2 = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1'],
            capture_output=True, text=True
        )
        changed_files = result2.stdout.strip().split('\n') if result2.stdout.strip() else []

        src_changed = any(f.startswith('src/') for f in changed_files)
        test_changed = any(f.startswith('tests/') for f in changed_files)
        req_changed = any(f == 'requirements.txt' for f in changed_files)
        workflow_changed = any(f.startswith('.github/workflows/') for f in changed_files)

        module = 'none'
        for f in changed_files:
            if 'pricing' in f:
                module = 'pricing'
                break
            elif 'cart' in f:
                module = 'cart'
                break
            elif 'inventory' in f:
                module = 'inventory'
                break

        return {
            'files_changed': files_changed,
            'lines_added': lines_added,
            'lines_deleted': lines_deleted,
            'src_changed': int(src_changed),
            'test_changed': int(test_changed),
            'req_changed': int(req_changed),
            'workflow_changed': int(workflow_changed),
            'module': module,
        }
    except Exception:
        return {
            'files_changed': 0, 'lines_added': 0, 'lines_deleted': 0,
            'src_changed': 0, 'test_changed': 0,
            'req_changed': 0, 'workflow_changed': 0,
            'module': 'none',
        }


def load_data(real_path: Path, generated_path: Path) -> pd.DataFrame:
    """Load and combine real and generated data."""
    dfs = []

    if real_path.exists():
        df_real = pd.read_csv(real_path)
        df_real['source'] = 'real'
        dfs.append(df_real)

    if generated_path.exists():
        df_gen = pd.read_csv(generated_path)
        df_gen['source'] = 'generated'
        dfs.append(df_gen)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # Ensure all expected columns exist
    for col in ['req_changed', 'workflow_changed']:
        if col not in df.columns:
            df[col] = 0

    # Feature engineering
    df['total_lines'] = df['lines_added'] + df['lines_deleted']
    df['is_pricing'] = (df['module'] == 'pricing').astype(int)
    df['is_cart'] = (df['module'] == 'cart').astype(int)
    df['is_inventory'] = (df['module'] == 'inventory').astype(int)

    # Time features
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', utc=True)
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek

    # Sort by time for temporal split
    df = df.sort_values('timestamp').reset_index(drop=True)

    return df


def prepare_features(df: pd.DataFrame) -> tuple:
    """Prepare feature matrix X and labels y."""
    feature_cols = [
        'files_changed', 'lines_added', 'lines_deleted', 'total_lines',
        'src_changed', 'test_changed', 'req_changed', 'workflow_changed',
        'is_pricing', 'is_cart', 'is_inventory',
        'hour', 'day_of_week',
    ]

    X = df[feature_cols].fillna(0)
    y = df['label']

    return X, y, feature_cols


def main():
    real_path = Path('ml/data/real_runs.csv')
    generated_path = Path('ml/data/generated_runs.csv')

    df = load_data(real_path, generated_path)
    if df.empty:
        print("No data found")
        return

    print(f"Total samples: {len(df)}")
    print(f"Real: {len(df[df['source']=='real'])}, Generated: {len(df[df['source']=='generated'])}")
    print(f"Failures: {df['label'].sum()}, Successes: {len(df) - df['label'].sum()}")

    X, y, feature_cols = prepare_features(df)

    print("\nFeature columns:", feature_cols)
    print("\nClass distribution:")
    print(y.value_counts().sort_index())

    # Save processed data
    output_path = Path('ml/data/processed.csv')
    df.to_csv(output_path, index=False)
    print(f"\nSaved processed data to {output_path}")


if __name__ == '__main__':
    main()