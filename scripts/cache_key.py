#!/usr/bin/env python3
"""
Cache key generator for modules based on content hashes including transitive dependencies.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Set

# Import the dep_graph functions
sys.path.insert(0, str(Path(__file__).parent))
from dep_graph import build_dep_graph, transitive_deps


def file_hash(filepath: Path) -> str:
    """Compute SHA256 hash of a file's content."""
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def module_hash(module: str, graph: Dict[str, List[str]], src_dir: Path, cache: Dict[str, str] = None) -> str:
    """Compute hash for a module including all its transitive dependencies."""
    if cache is None:
        cache = {}

    if module in cache:
        return cache[module]

    # Hash of the module's own source
    module_file = src_dir / f"{module}.py"
    own_hash = file_hash(module_file) if module_file.exists() else "missing"

    # Hashes of all transitive dependencies
    dep_hashes = []
    for dep in sorted(transitive_deps(graph, module) - {module}):
        dep_hashes.append(module_hash(dep, graph, src_dir, cache))

    # Combine own hash with dependency hashes
    combined = own_hash + ''.join(dep_hashes)
    result = hashlib.sha256(combined.encode()).hexdigest()[:16]
    cache[module] = result
    return result


def all_module_hashes(src_dir: Path) -> Dict[str, str]:
    """Compute transitive hashes for all modules in src_dir."""
    graph = build_dep_graph(src_dir)
    hashes = {}
    for module in sorted(graph.keys()):
        hashes[module] = module_hash(module, graph, src_dir)
    return hashes


def combined_hash(hashes: Dict[str, str]) -> str:
    """Compute a combined hash of all module hashes."""
    combined = ''.join(f"{k}:{v}" for k, v in sorted(hashes.items()))
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def main():
    src_dir = Path('src')
    if not src_dir.exists():
        print(f"Error: {src_dir} not found", file=sys.stderr)
        sys.exit(1)

    hashes = all_module_hashes(src_dir)

    if len(sys.argv) > 1:
        if sys.argv[1] == '--module' and len(sys.argv) > 2:
            module = sys.argv[2]
            print(hashes.get(module, "unknown"))
        elif sys.argv[1] == '--combined':
            print(combined_hash(hashes))
        elif sys.argv[1] == '--json':
            print(json.dumps(hashes, indent=2))
    else:
        print("Module Hashes (including transitive deps):")
        for module, h in sorted(hashes.items()):
            print(f"  {module}: {h}")
        print(f"\nCombined: {combined_hash(hashes)}")


if __name__ == '__main__':
    main()