#!/usr/bin/env python3
"""
Dependency graph builder for src/ modules.
Parses Python imports using AST to build a module dependency graph.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set


def parse_imports(filepath: Path) -> List[str]:
    """Extract imported module names from a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()

    tree = ast.parse(content)
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


def build_dep_graph(src_dir: Path) -> Dict[str, List[str]]:
    """Build dependency graph for all Python modules in src_dir."""
    modules = {}
    for py_file in src_dir.glob('*.py'):
        if py_file.name == '__init__.py':
            continue
        module_name = py_file.stem
        imports = parse_imports(py_file)
        # Filter to only local src modules
        local_imports = [imp for imp in imports if imp.startswith('src.')]
        # Convert src.pricing -> pricing
        local_imports = [imp.replace('src.', '') for imp in local_imports]
        modules[module_name] = local_imports
    return modules


def transitive_deps(graph: Dict[str, List[str]], module: str, visited: Set[str] = None) -> Set[str]:
    """Get all transitive dependencies of a module."""
    if visited is None:
        visited = set()
    if module in visited:
        return visited
    visited.add(module)
    for dep in graph.get(module, []):
        transitive_deps(graph, dep, visited)
    return visited


def reverse_deps(graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Build reverse dependency graph (dependents)."""
    rev = {k: [] for k in graph}
    for module, deps in graph.items():
        for dep in deps:
            if dep in rev:
                rev[dep].append(module)
    return rev


def affected_modules(graph: Dict[str, List[str]], changed: List[str]) -> Set[str]:
    """Get all modules affected by changes (changed + their dependents)."""
    rev = reverse_deps(graph)
    affected = set(changed)
    for mod in changed:
        # Add transitive dependents
        queue = list(rev.get(mod, []))
        while queue:
            m = queue.pop(0)
            if m not in affected:
                affected.add(m)
                queue.extend(rev.get(m, []))
    return affected


def main():
    src_dir = Path('src')
    if not src_dir.exists():
        print(f"Error: {src_dir} not found", file=sys.stderr)
        sys.exit(1)

    graph = build_dep_graph(src_dir)

    if len(sys.argv) > 1 and sys.argv[1] == '--changed':
        changed = sys.argv[2:] if len(sys.argv) > 2 else []
        affected = affected_modules(graph, changed)
        print(' '.join(sorted(affected)))
    else:
        print("Dependency Graph:")
        for module, deps in sorted(graph.items()):
            print(f"  {module} -> {deps if deps else '(none)'}")

        print("\nTransitive Dependencies:")
        for module in sorted(graph.keys()):
            deps = transitive_deps(graph, module) - {module}
            print(f"  {module} -> {sorted(deps) if deps else '(none)'}")

        print("\nReverse Dependencies (Dependents):")
        rev = reverse_deps(graph)
        for module, deps in sorted(rev.items()):
            print(f"  {module} <- {deps if deps else '(none)'}")


if __name__ == '__main__':
    main()