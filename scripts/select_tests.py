#!/usr/bin/env python3
"""
Dynamic test selector based on changed files and dependency graph.
Maps source file changes to relevant tests, with safe fallbacks.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Set

# Import dep_graph functions
sys.path.insert(0, str(Path(__file__).parent))
from dep_graph import build_dep_graph, affected_modules


SOURCE_TO_TEST_MAP = {
    'pricing': ['tests/test_pricing.py', 'tests/test_cart.py'],
    'cart': ['tests/test_cart.py'],
    'inventory': ['tests/test_inventory.py'],
}

FALLBACK_FILES = {
    'requirements.txt',
    'pytest.ini',
    '.github/workflows/ci.yml',
    'scripts/dep_graph.py',
    'scripts/cache_key.py',
    'scripts/select_tests.py',
    'scripts/summarize_log.py',
}


def get_changed_files(base_ref: str = 'HEAD~1') -> List[str]:
    """Get changed files from git diff."""
    try:
        # For PR: use base branch; for push: use previous commit
        if os.environ.get('GITHUB_EVENT_NAME') == 'pull_request':
            base = os.environ.get('GITHUB_BASE_REF', 'main')
            result = subprocess.run(
                ['git', 'diff', '--name-only', f'origin/{base}...HEAD'],
                capture_output=True, text=True, check=True
            )
        else:
            result = subprocess.run(
                ['git', 'diff', '--name-only', f'{base_ref}...HEAD'],
                capture_output=True, text=True, check=True
            )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        return []


def map_changes_to_tests(changed_files: List[str]) -> List[str]:
    """Map changed source files to test files using dependency graph."""
    if not changed_files:
        return ['all']

    # Check for fallback-triggering files
    for f in changed_files:
        if f in FALLBACK_FILES or f.startswith('.github/') or f.startswith('scripts/'):
            return ['all']

    src_dir = Path('src')
    if not src_dir.exists():
        return ['all']

    graph = build_dep_graph(src_dir)

    # Find affected modules
    changed_modules = []
    for f in changed_files:
        if f.startswith('src/') and f.endswith('.py'):
            module = Path(f).stem
            if module in graph:
                changed_modules.append(module)
        elif f.startswith('tests/') and f.endswith('.py'):
            # Direct test file change - run that test
            return [f]

    if not changed_modules:
        return ['all']

    # Get affected modules (changed + transitive dependents)
    affected = affected_modules(graph, changed_modules)

    # Map to test files
    test_files = set()
    for module in affected:
        test_files.update(SOURCE_TO_TEST_MAP.get(module, []))

    if not test_files:
        return ['all']

    return sorted(test_files)


def select_tests() -> List[str]:
    """Main entry point - returns list of test files/nodes to run."""
    # Always run full suite on main branch pushes
    if os.environ.get('GITHUB_REF') == 'refs/heads/main':
        return ['all']

    # For PRs or other pushes
    changed = get_changed_files()

    if not changed:
        return ['all']

    tests = map_changes_to_tests(changed)

    if tests == ['all']:
        return ['all']

    return tests


def main():
    tests = select_tests()

    if tests == ['all']:
        print("all")
    else:
        print(' '.join(tests))

    # Debug output
    print(f"::notice::Changed files: {get_changed_files()}", file=sys.stderr)
    print(f"::notice::Selected tests: {tests}", file=sys.stderr)


if __name__ == '__main__':
    main()