# SmartCI Assignment Submission

**USN:** 24BTRAO004  
**Name:** Ashwin Lahkar  
**Repository:** https://github.com/ghoulraider13-rgb/smartci

## Lab Completion Status

- ✅ **Lab 0:** Project skeleton setup (VS Code, Python 3.12, Git, Copilot, virtual environment, folder structure, GitHub repo)
- ✅ **Lab 1:** App and tests (pricing.py, cart.py, inventory.py, 9 pytest tests - all passing)
- ✅ **Lab 2:** Baseline CI pipeline (GitHub Actions workflow with green and red runs)

## GitHub Actions - Red Run Explanation

**What is the use of a red run?**

A red run (failed CI build) serves several critical purposes:

1. **Validates CI Pipeline Works**: Confirms the CI system correctly detects and reports failures. A pipeline that never fails might be misconfigured or not actually testing anything.

2. **Catches Regressions**: When code changes break existing functionality, the red run immediately surfaces the regression before it reaches production.

3. **Failure Visibility**: Shows exactly where and why the build failed (which test, which assertion, stack trace) — enabling rapid debugging.

4. **Enforces Quality Gates**: Prevents merging broken code by making failures visible in PR checks.

5. **Documents Expected Behavior**: The failing test documents what the correct behavior should be (in this case: `apply_discount(100, 0) == 100.0`, not `101.0`).

## Screenshots Required for Submission

Please capture the following from the GitHub repository:

1. **Repository Overview** - Main page showing commits and tags (lab1, lab2)
2. **Actions Tab - All Runs** - Showing both green (success) and red (failure) runs
3. **Red Run Details** - Click on the failed run "Break test for red run experiment" to show:
   - The failed step "Run tests"
   - Error log showing: `assert 100.0 == 101.0` in `tests/test_pricing.py:10`
   - `FAILED tests/test_pricing.py::test_discount_boundaries - assert 100.0 == 101.0`
4. **Green Run Details** - Click on any successful run showing all 9 tests passing

## Tags Created
- `lab1` - After Lab 1 completion (app + tests)
- `lab2` - After Lab 2 completion (CI pipeline with green + red runs)

## Key Files
- `.github/workflows/ci.yml` - CI pipeline configuration
- `src/pricing.py` - Discount and tax functions
- `src/cart.py` - Shopping cart with pricing integration
- `src/inventory.py` - Stock management
- `tests/test_pricing.py` - 5 tests (basic, boundaries, invalid, tax)
- `tests/test_cart.py` - 2 tests (discount total, empty cart)
- `tests/test_inventory.py` - 3 tests (add, remove, remove too much)