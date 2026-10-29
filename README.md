# SmartCI Assignment Submission

**USN:** 24BTRAO004  
**Name:** Ashwin Lahkar  
**Repository:** https://github.com/ghoulraider13-rgb/smartci

## Lab Completion Status

- ✅ **Lab 0:** Project skeleton setup (VS Code, Python 3.12, Git, Copilot, virtual environment, folder structure, GitHub repo)
- ✅ **Lab 1:** App and tests (pricing.py, cart.py, inventory.py, 9 pytest tests - all passing)
- ✅ **Lab 2:** Baseline CI pipeline (GitHub Actions workflow with green and red runs)
- ✅ **Lab 3:** Smart Build-Cache Invalidation
- ✅ **Lab 4:** Dynamic Test-Subset Routing
- ✅ **Lab 5:** LLM-Based Build/Error-Log Summarization
- ✅ **Lab 6:** Build-Failure Prediction

## GitHub Actions - Red Run Explanation

**What is the use of a red run?**

A red run (failed CI build) serves several critical purposes:

1. **Validates CI Pipeline Works**: Confirms the CI system correctly detects and reports failures. A pipeline that never fails might be misconfigured or not actually testing anything.

2. **Catches Regressions**: When code changes break existing functionality, the red run immediately surfaces the regression before it reaches production.

3. **Failure Visibility**: Shows exactly where and why the build failed (which test, which assertion, stack trace) — enabling rapid debugging.

4. **Enforces Quality Gates**: Prevents merging broken code by making failures visible in PR checks.

5. **Documents Expected Behavior**: The failing test documents what the correct behavior should be (in this case: `apply_discount(100, 0) == 100.0`, not `101.0`).

## Task 3: Smart Build-Cache Invalidation

**Goal:** Cache what is safe to reuse across CI runs, and invalidate only what a change actually affects.

**How to run:**
```bash
# View dependency graph
python scripts/dep_graph.py

# View module hashes
python scripts/cache_key.py

# Run CI (triggers on push/PR automatically)
```

**Files:** `scripts/dep_graph.py`, `scripts/cache_key.py`

**Tag:** `lab3`

## Task 4: Dynamic Test-Subset Routing

**Goal:** Run only the tests relevant to a change, with safe fallbacks to the full suite.

**How to run:**
```bash
# View selected tests for current diff
python scripts/select_tests.py

# Run tests (CI auto-runs on push/PR)
python scripts/select_tests.py | xargs pytest
```

**Files:** `scripts/select_tests.py`, `tests/test_select_tests.py`

**Tag:** `lab4`

## Task 5: LLM-Based Build/Error-Log Summarization

**Goal:** Turn a noisy `build.log` into a short, structured summary of failures.

**How to run:**
```bash
# Generate a failing build.log, then summarize
python scripts/summarize_log.py

# With LLM key (set as GitHub Secret ANTHROPIC_API_KEY or OPENAI_API_KEY):
ANTHROPIC_API_KEY=xxx python scripts/summarize_log.py
```

**Files:** `scripts/summarize_log.py`

**Tag:** `lab5`

## Task 6: Build-Failure Prediction

**Goal:** Predict build-failure likelihood before running tests, warn-only (never blocks).

**How to run:**
```bash
# Export real CI history (run in repo root with gh CLI)
python ml/export_real_runs.py

# Generate synthetic labelled data
python ml/generate_synthetic.py

# Train the model
python ml/train.py

# Predict current commit
python ml/predict.py
```

**Files:** `ml/features.py`, `ml/train.py`, `ml/predict.py`, `ml/export_real_runs.py`, `ml/generate_synthetic.py`, `ml/requirements.txt`

**Tag:** `lab6`
