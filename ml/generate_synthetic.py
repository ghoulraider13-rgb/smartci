#!/usr/bin/env python3
"""
Generate synthetic labelled CI runs by creating commits with deliberate faults.
This is for Task 5 to augment the small real dataset.
"""

import os
import subprocess
import csv
import random
import tempfile
import shutil
from pathlib import Path
from datetime import datetime


# Fault injection patterns
FAULTS = [
    # (description, file, search, replace, expected_failure)
    ("break_discount_boundary", "tests/test_pricing.py",
     "assert apply_discount(100, 0) == 100.0",
     "assert apply_discount(100, 0) == 101.0", True),

    ("break_tax_calculation", "src/pricing.py",
     "return round(price * (1 + rate), 2)",
     "return round(price * (1 + rate) * 2, 2)", True),

    ("break_import", "src/cart.py",
     "from src.pricing import apply_discount, add_tax",
     "from src.pricing import apply_discount, add_tax, nonexistent", True),

    ("break_inventory_validation", "src/inventory.py",
     "if self.stock.get(name, 0) < qty:",
     "if self.stock.get(name, 0) <= qty:", True),

    ("correct_add_comment_apply_discount", "src/pricing.py",
     "def apply_discount(price, percent):",
     "def apply_discount(price, percent):\n    # Added comment", False),

    ("correct_add_comment_add_tax", "src/pricing.py",
     "def add_tax(price, rate=0.18):",
     "def add_tax(price, rate=0.18):\n    # Added comment", False),

    ("correct_add_comment_inventory", "src/inventory.py",
     "    def get_stock(self, name):",
     "    def get_stock(self, name):\n        # Added comment", False),

    ("correct_add_comment_test", "tests/test_pricing.py",
     "def test_tax_default():",
     "def test_tax_default():\n    # Added comment", False),
]


def run_tests():
    """Run pytest and return (passed, output)."""
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', '-v'],
            capture_output=True, text=True, timeout=60
        )
        return result.returncode == 0, result.stdout
    except subprocess.TimeoutExpired:
        return False, "timeout"


def apply_fault(filepath, search, replace):
    """Apply a fault to a file."""
    content = filepath.read_text()
    if search not in content:
        return False
    new_content = content.replace(search, replace)
    filepath.write_text(new_content)
    return True


def revert_fault(filepath, search, replace):
    """Revert a fault in a file."""
    content = filepath.read_text()
    if replace not in content:
        return False
    new_content = content.replace(replace, search)
    filepath.write_text(new_content)
    return True


def get_git_diff_stats():
    """Get git diff stats for current changes."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--stat'],
            capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()
        files_changed = 0
        lines_added = 0
        lines_deleted = 0
        src_changed = False
        test_changed = False
        module = 'none'

        for line in output.split('\n'):
            if 'file' in line and 'changed' in line:
                parts = line.split(',')
                if len(parts) >= 3:
                    files_changed = int(parts[0].strip().split()[0])
                    lines_added = int(parts[1].strip().split()[0])
                    lines_deleted = int(parts[2].strip().split()[0])

        # Check which files changed
        result2 = subprocess.run(
            ['git', 'diff', '--name-only'],
            capture_output=True, text=True, check=True
        )
        for fname in result2.stdout.strip().split('\n'):
            if fname.startswith('src/'):
                src_changed = True
                if 'pricing' in fname:
                    module = 'pricing'
                elif 'cart' in fname:
                    module = 'cart'
                elif 'inventory' in fname:
                    module = 'inventory'
            elif fname.startswith('tests/'):
                test_changed = True

        return {
            'files_changed': files_changed,
            'lines_added': lines_added,
            'lines_deleted': lines_deleted,
            'src_changed': int(src_changed),
            'test_changed': int(test_changed),
            'module': module,
        }
    except subprocess.CalledProcessError:
        return {
            'files_changed': 0, 'lines_added': 0, 'lines_deleted': 0,
            'src_changed': 0, 'test_changed': 0, 'module': 'none',
        }


def main():
    repo_root = Path('.')
    output_path = Path('ml/data/generated_runs.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    num_samples = 20  # Generate 20 synthetic runs

    print(f"Generating {num_samples} synthetic runs...")

    for i in range(num_samples):
        # Pick a fault
        desc, filepath, search, replace, should_fail = random.choice(FAULTS)
        full_path = repo_root / filepath

        # Apply fault
        if not apply_fault(full_path, search, replace):
            print(f"  [{i+1}/{num_samples}] Could not apply {desc}")
            continue

        # Get diff stats
        stats = get_git_diff_stats()

        # Run tests
        passed, output = run_tests()
        actual_fail = not passed
        label = 1 if actual_fail else 0

        # Revert fault
        revert_fault(full_path, search, replace)

        row = {
            'run_id': f'gen_{i:04d}',
            'sha': f'gen{i:04d}',
            'timestamp': datetime.now().isoformat() + 'Z',
            'conclusion': 'failure' if actual_fail else 'success',
            'label': label,
            'files_changed': stats['files_changed'],
            'lines_added': stats['lines_added'],
            'lines_deleted': stats['lines_deleted'],
            'src_changed': stats['src_changed'],
            'test_changed': stats['test_changed'],
            'module': stats['module'],
            'event': 'push',
            'source': 'generated',
            'fault_type': desc,
            'expected_fail': int(should_fail),
            'actual_fail': int(actual_fail),
        }
        rows.append(row)

        status = "FAIL" if actual_fail else "PASS"
        expected = "FAIL" if should_fail else "PASS"
        match = "✓" if (should_fail == actual_fail) else "✗"
        print(f"  [{i+1}/{num_samples}] {desc}: {status} (expected {expected}) {match}")

    # Write CSV
    fieldnames = ['run_id', 'sha', 'timestamp', 'conclusion', 'label',
                  'files_changed', 'lines_added', 'lines_deleted',
                  'src_changed', 'test_changed', 'module', 'event', 'source',
                  'fault_type', 'expected_fail', 'actual_fail']

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nGenerated {len(rows)} runs to {output_path}")
    fails = sum(1 for r in rows if r['label'] == 1)
    print(f"  Failures: {fails}, Successes: {len(rows) - fails}")


if __name__ == '__main__':
    main()