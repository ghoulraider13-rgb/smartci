#!/usr/bin/env python3
"""
LLM-based build log summarizer with deterministic fallback.
Extracts failure info from pytest logs and generates structured summary.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any


def extract_failure_region(log_path: Path) -> str:
    """Extract the relevant failure region from build.log."""
    content = log_path.read_text()

    # Find the FAILURES section
    failures_match = re.search(r'=+ FAILURES =+.*?(?=\n=+ |\n==+ |\n\Z)', content, re.DOTALL)
    if failures_match:
        failures_text = failures_match.group(0)
    else:
        failures_text = ""

    # Find the short test summary
    summary_match = re.search(r'=+ (?:short test summary info|FAILED|ERROR) =+.*', content, re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(0)
    else:
        summary_text = ""

    # Also get the last ~50 lines for context
    lines = content.splitlines()
    tail = '\n'.join(lines[-50:]) if len(lines) > 50 else content

    # Combine, deduplicate
    combined = failures_text + '\n\n' + summary_text + '\n\n--- TAIL ---\n' + tail

    # Truncate to reasonable size for LLM (max ~4000 chars)
    return combined[:4000]


def redact_secrets(text: str) -> str:
    """Redact potential secrets from log text."""
    # Redact common secret patterns
    patterns = [
        (r'(?i)(api[_-]?key|token|secret|password|auth)[\s:=]+[\w\-]{20,}', r'\1=***REDACTED***'),
        (r'gh[pousr]_[A-Za-z0-9]{36,}', '***GITHUB_TOKEN***'),
        (r'(?i)bearer\s+[\w\-]{20,}', 'Bearer ***REDACTED***'),
        (r'(?i)authorization:\s*[\w\-]{20,}', 'Authorization: ***REDACTED***'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def deterministic_summary(log_path: Path) -> Dict[str, Any]:
    """Generate a deterministic regex-based summary (fallback)."""
    content = log_path.read_text()

    result = {
        "what_failed": "Unknown",
        "where": "Unknown",
        "expected_vs_actual": "Unknown",
        "probable_cause": "Unknown",
        "suggested_fix": "Unknown",
    }

    # Extract failed test name
    failed_match = re.search(r'(tests/\S+::\w+)\s+FAILED', content)
    if not failed_match:
        failed_match = re.search(r'FAILED\s+(tests/\S+::\w+)', content)
    if failed_match:
        result["what_failed"] = failed_match.group(1)

    # Extract file:line from traceback
    file_line_match = re.search(r'(\S+\.py):(\d+):', content)
    if file_line_match:
        result["where"] = f"{file_line_match.group(1)}:{file_line_match.group(2)}"

    # Extract assertion failure (expected vs actual)
    assert_match = re.search(r'assert\s+(.+?)\s+==\s+(.+)', content)
    if assert_match:
        result["expected_vs_actual"] = f"Expected {assert_match.group(2).strip()}, got {assert_match.group(1).strip()}"

    # Extract error type
    error_match = re.search(r'(?:^|\n)(\w+Error|Exception|AssertionError):', content)
    if error_match:
        result["probable_cause"] = f"{error_match.group(1)} raised"

    # Try to infer cause from common patterns
    if 'ImportError' in content or 'ModuleNotFoundError' in content:
        result["probable_cause"] = "Import error - missing dependency or broken import"
        result["suggested_fix"] = "Check imports and dependencies in requirements.txt"
    elif 'AssertionError' in content and 'expected' in result["expected_vs_actual"].lower():
        result["probable_cause"] = "Assertion failed - code behavior doesn't match test expectation"
        result["suggested_fix"] = "Review the failing assertion and fix the code or update the test"
    elif 'ValueError' in content:
        result["probable_cause"] = "ValueError - invalid input or boundary condition"
        result["suggested_fix"] = "Add input validation or fix boundary handling"

    return result


def llm_summary(log_path: Path, api_key: str, provider: str = "anthropic") -> Optional[Dict[str, Any]]:
    """Call LLM API to summarize the log."""
    try:
        import requests
    except ImportError:
        return None

    log_text = extract_failure_region(log_path)
    log_text = redact_secrets(log_text)

    prompt = f"""You are a CI build log analyzer. Given a pytest failure log, produce a structured summary.

Log excerpt:
{log_text}

Return ONLY a JSON object with these exact keys:
- what_failed: The test name that failed (e.g., "tests/test_pricing.py::test_discount_boundaries")
- where: File and line number (e.g., "tests/test_pricing.py:10")
- expected_vs_actual: What the test expected vs what it got (e.g., "Expected 100.0, got 101.0")
- probable_cause: One-sentence likely root cause based ONLY on log evidence
- suggested_fix: One-sentence actionable fix suggestion

Rules:
- Use ONLY facts present in the log
- If something is not in the log, use "unknown"
- Do not speculate beyond the log content
- Keep each field concise (max 200 chars)"""

    if provider == "anthropic":
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
        }
        url = "https://api.anthropic.com/v1/messages"
    else:
        return None

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        if resp.status_code != 200:
            return None
        result = resp.json()
        text = result.get("content", [{}])[0].get("text", "{}")
        return json.loads(text)
    except Exception:
        return None


def main():
    log_path = Path("build.log")
    if not log_path.exists():
        print("build.log not found", file=sys.stderr)
        sys.exit(1)

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    provider = "anthropic" if os.environ.get("ANTHROPIC_API_KEY") else "openai"

    # Try LLM first if key available
    summary = None
    if api_key:
        summary = llm_summary(log_path, api_key, provider)

    # Fallback to deterministic
    if summary is None:
        summary = deterministic_summary(log_path)

    # Output as GitHub step summary
    md = f"""## Build Failure Summary

| Field | Value |
|-------|-------|
| **What Failed** | {summary['what_failed']} |
| **Where** | {summary['where']} |
| **Expected vs Actual** | {summary['expected_vs_actual']} |
| **Probable Cause** | {summary['probable_cause']} |
| **Suggested Fix** | {summary['suggested_fix']} |

*Generated by {'LLM' if api_key else 'deterministic fallback'} summarizer*
"""
    # Write to GITHUB_STEP_SUMMARY
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write(md)

    # Also print to stdout for logs
    print(md)


if __name__ == "__main__":
    main()