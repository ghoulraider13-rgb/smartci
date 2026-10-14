# SmartCI Assignment — Final Submission

**USN:** 24BTRAO004  
**Name:** Ashwin Lahkar  
**Repository:** https://github.com/ghoulraider13-rgb/smartci  
**Branch:** `main`  
**Tags:** `lab1`, `lab2`

---

## ✅ Lab Completion Checklist

| Lab | Requirement | Status |
|-----|-------------|--------|
| **Lab 0** | VS Code, Python 3.12, Git, Copilot extensions, virtual env, folder structure, GitHub repo | ✅ Done |
| **Lab 1** | `src/pricing.py`, `src/cart.py`, `src/inventory.py` + 9 pytest tests (all pass) | ✅ Done |
| **Lab 2** | `.github/workflows/ci.yml` with green + red runs | ✅ Done |

---

## 📸 Screenshots (Attached)

| # | File | Description |
|---|------|-------------|
| 1 | `Screenshot (48).png` | **Repository main page** — commits, tags (lab1, lab2) visible |
| 2 | `Screenshot (49).png` | **Actions tab** — all 3 runs (2 green ✅, 1 red ❌) |
| 3 | `Screenshot (50).png` | **Red run details** — failed "Run tests" step showing `assert 100.0 == 101.0` |
| 4 | `Screenshot (51).png` | **Green run details** — successful run showing `9 passed in 0.03s` |

> **Paths on your machine:**  
> `C:\Users\Ashwin\OneDrive\Pictures\Screenshots\Screenshot (48).png`  
> `C:\Users\Ashwin\OneDrive\Pictures\Screenshots\Screenshot (49).png`  
> `C:\Users\Ashwin\OneDrive\Pictures\Screenshots\Screenshot (50).png`  
> `C:\Users\Ashwin\OneDrive\Pictures\Screenshots\Screenshot (51).png`

---

## 🔴 Red Run — Purpose & Explanation

**What is the use of a red (failed) CI run?**

1. **Validates the CI pipeline works** — A pipeline that never fails may be misconfigured or not actually testing anything. The red run proves the system detects and reports failures correctly.

2. **Catches regressions immediately** — When a change breaks existing behavior (e.g., `apply_discount(100, 0)` returning `101.0` instead of `100.0`), the red run surfaces it before merge.

3. **Provides failure visibility** — The logs show exactly *which* test failed (`test_discount_boundaries`), *where* (`tests/test_pricing.py:10`), and *why* (`assert 100.0 == 101.0`), enabling rapid debugging.

4. **Enforces quality gates** — Failed runs block PR merges (when branch protection is enabled), preventing broken code from reaching `main`.

5. **Documents expected behavior** — The failing test itself serves as executable documentation: `apply_discount(100, 0) == 100.0` is the correct contract.

> In this assignment, the red run was intentionally triggered by changing the boundary assertion from `100.0` to `101.0`, then fixed in the subsequent commit ("Fix test - restore correct boundary value"), demonstrating the full red→green cycle.

---

## 📂 Key Files in Repository

```
smartci/
├── .github/workflows/ci.yml       # CI pipeline (checkout, setup-python, install, test)
├── src/
│   ├── __init__.py
│   ├── pricing.py                 # apply_discount(), add_tax()
│   ├── cart.py                    # Cart class (uses pricing)
│   └── inventory.py               # Inventory class
├── tests/
│   ├── test_pricing.py            # 5 tests (basic, boundaries, invalid, tax)
│   ├── test_cart.py               # 2 tests (discount total, empty cart)
│   └── test_inventory.py          # 3 tests (add, remove, remove-too-much)
├── requirements.txt               # pytest, requests
├── pytest.ini                     # pythonpath = .
├── .gitignore                     # .venv/, __pycache__/, .pytest_cache/, build.log
└── README.md                      # This submission document
```

---

## 🏷️ Git Tags

| Tag | Commit | Description |
|-----|--------|-------------|
| `lab1` | `803912e` | Lab 0 + Lab 1 complete (app + tests) |
| `lab2` | `daa3a0a` | Lab 2 complete (CI pipeline with green + red runs) |

---

## 🔗 Quick Links

- **Repository:** https://github.com/ghoulraider13-rgb/smartci
- **Actions (CI runs):** https://github.com/ghoulraider13-rgb/smartci/actions
- **Tags:** https://github.com/ghoulraider13-rgb/smartci/tags

---

**Submitted by:** Ashwin Lahkar (24BTRAO004)  
**Date:** October 14, 2026