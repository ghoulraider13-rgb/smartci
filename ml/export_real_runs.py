#!/usr/bin/env python3
"""
Export real CI history from GitHub Actions.
"""

import json
import os
import subprocess
import csv
import sys
from pathlib import Path
from datetime import datetime


def get_ci_runs():
    """Get CI runs from GitHub CLI."""
    try:
        result = subprocess.run(
            ['gh', 'run', 'list', '--branch', 'main', '--limit', '100', '--json',
             'databaseId,conclusion,createdAt,headSha,headBranch,event'],
            capture_output=True, text=True, check=True
        )
        import json
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error fetching CI runs: {e}", file=sys.stderr)
        return []


def get_run_jobs(run_id):
    """Get jobs for a specific run."""
    try:
        result = subprocess.run(
            ['gh', 'run', 'view', str(run_id), '--json', 'jobs'],
            capture_output=True, text=True, check=True
        )
        import json
        data = json.loads(result.stdout)
        return data.get('jobs', [])
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []


def get_commit_info(sha):
    """Get commit info (files changed, lines added/deleted)."""
    try:
        # Get diff stats
        result = subprocess.run(
            ['git', 'show', '--stat', '--oneline', sha],
            capture_output=True, text=True, check=True
        )
        output = result.stdout
        lines = output.split('\n')

        files_changed = 0
        lines_added = 0
        lines_deleted = 0
        src_changed = False
        test_changed = False
        module = 'none'

        for line in lines:
            if 'file' in line and 'changed' in line:
                # Parse: " X files changed, Y insertions(+), Z deletions(-)"
                parts = line.split(',')
                if len(parts) >= 3:
                    files_changed = int(parts[0].strip().split()[0])
                    lines_added = int(parts[1].strip().split()[0])
                    lines_deleted = int(parts[2].strip().split()[0])

            # Track which files changed
            if line.strip().startswith('src/'):
                src_changed = True
                if 'pricing' in line:
                    module = 'pricing'
                elif 'cart' in line:
                    module = 'cart'
                elif 'inventory' in line:
                    module = 'inventory'
            elif line.strip().startswith('tests/'):
                test_changed = True

        return {
            'files_changed': files_changed,
            'lines_added': lines_added,
            'lines_deleted': lines_deleted,
            'src_changed': src_changed,
            'test_changed': test_changed,
            'module': module,
        }
    except subprocess.CalledProcessError:
        return {
            'files_changed': 0,
            'lines_added': 0,
            'lines_deleted': 0,
            'src_changed': False,
            'test_changed': False,
            'module': 'none',
        }


def main():
    import sys

    runs = get_ci_runs()
    if not runs:
        print("No CI runs found", file=sys.stderr)
        sys.exit(1)

    # Get commit info for each run
    rows = []
    for run in runs:
        sha = run['headSha']
        conclusion = run['conclusion']
        created_at = run['createdAt']

        # Skip in-progress runs
        if conclusion is None:
            continue

        commit_info = get_commit_info(sha)

        row = {
            'run_id': run['databaseId'],
            'sha': sha[:8],
            'timestamp': created_at,
            'conclusion': conclusion,
            'label': 1 if conclusion == 'failure' else 0,
            'files_changed': commit_info['files_changed'],
            'lines_added': commit_info['lines_added'],
            'lines_deleted': commit_info['lines_deleted'],
            'src_changed': int(commit_info['src_changed']),
            'test_changed': int(commit_info['test_changed']),
            'module': commit_info['module'],
            'event': run['event'],
            'source': 'real',
        }
        rows.append(row)

    # Write to CSV
    output_path = Path('ml/data/real_runs.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ['run_id', 'sha', 'timestamp', 'conclusion', 'label',
                  'files_changed', 'lines_added', 'lines_deleted',
                  'src_changed', 'test_changed', 'module', 'event', 'source']

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} real runs to {output_path}")


if __name__ == '__main__':
    main()