# Agile / Project-Management Tool Exploration Report

**Student Name:** Ashwin Lahkar  
**USN:** 24BTRAO004  
**Repository:** [ghoulraider13-rgb/smartci](https://github.com/ghoulraider13-rgb/smartci)  
**Tool Explored:** GitHub Projects (v2), GitHub Issues, & GitHub Actions Workflows  
**Submission Deadline:** 31st October 2026  
**Evaluation:** 10 Marks (Mapped to CO1–CO5)

---

## 1. Introduction & Tool Selection

For this Agile & Project-Management exploration, **GitHub Projects (v2)** integrated with **GitHub Issues** and **GitHub Actions** was selected and applied directly to the **SmartCI** repository (`ghoulraider13-rgb/smartci`).

GitHub Projects provides native Agile planning capabilities directly alongside source code and CI/CD pipelines, including:
- **Kanban & Sprint Boards** with customizable status columns (`Backlog`, `Todo`, `In Progress`, `In Review`, `Done`).
- **Iteration (Sprint) Tracking** with sprint milestones, burn-up/status insights, and velocity tracking via Story Points.
- **Custom Fields** for Story Points (Fibonacci scale), Priority (`High`, `Medium`, `Low`), and Issue Type (`User Story`, `Task`, `Bug`).
- **Issue Form Templates** (`.github/ISSUE_TEMPLATE/`) for standardized User Stories, Technical Tasks, and Bug Reports.
- **Automated Workflows** combining GitHub Projects' built-in event workflows and a custom GitHub Actions workflow (`.github/workflows/agile-board-sync.yml`).

---

## 2. Course Outcome (CO1–CO5) Mapping

| Course Outcome | Agile Activity Performed in SmartCI | Evidence in Repository |
| :--- | :--- | :--- |
| **CO1** | Understand Agile principles, iterative delivery, and Scrum roles/artifacts | Structured Product Backlog, Sprint 1 & Sprint 2 Milestones, and Definition of Done in `.github/pull_request_template.md` |
| **CO2** | Translate project requirements into User Stories with Acceptance Criteria | `.github/ISSUE_TEMPLATE/user_story.yml` and `[US]` GitHub Issues for Pricing, Cart, Inventory, Cache, Test Routing, and ML Prediction |
| **CO3** | Configure Agile boards, custom fields, and automated workflow transitions | `SmartCI Agile Sprint Board` (5-column Kanban), GitHub Project Workflows, and `.github/workflows/agile-board-sync.yml` |
| **CO4** | Plan, estimate, and track Sprints using Story Points and Milestones | Sprint 1 & Sprint 2 Milestones, Fibonacci Story Point estimates (`1, 2, 3, 5, 8`), and Sprint Board views |
| **CO5** | Reflect on team/CI integration, traceability, and continuous improvement | End-to-end traceability from User Story → PR → SmartCI (`ci.yml`) → Board Done column; Section 6 Learnings |

---

## 3. Boards & Workflows Configured

### 3.1 Kanban / Sprint Board (`SmartCI Agile Sprint Board`)
A GitHub Project (v2) board was configured with the following columns and custom fields:
- **Board Columns (Status):** `Backlog` → `Todo` → `In Progress` → `In Review` → `Done`
- **Views Configured:**
  1. **Board View (Kanban):** Visualizes all User Stories and Tasks across workflow stages.
  2. **Table / Backlog View:** Displays all items grouped by Sprint/Milestone with Story Points and Priority.
  3. **Current Sprint View:** Filtered to active Sprint items for daily stand-up tracking.

> **[INSERT SCREENSHOT 1: SmartCI Agile Sprint Board — Kanban Board View showing Backlog, Todo, In Progress, In Review, and Done columns]**

### 3.2 Automated Workflows
Two layers of workflow automation were configured:

1. **GitHub Projects Built-in Workflows:**
   - **Item added to project:** Automatically sets Status to `Todo` or `Backlog`.
   - **Item closed:** Automatically moves the card to `Done`.
   - **Item reopened:** Automatically moves the card back to `In Progress`.
   - **Pull request merged:** Automatically transitions linked issues/PRs to `Done`.
   - **Auto-add to project:** Automatically pulls new issues from `ghoulraider13-rgb/smartci` onto the board.

2. **Repository GitHub Actions Workflow (`.github/workflows/agile-board-sync.yml`):**
   - Triggers on `issues` (`opened`, `labeled`, `closed`, `reopened`) and `pull_request` (`opened`, `ready_for_review`, `closed`).
   - Auto-triages and applies `user-story`, `task`, or `bug` labels based on issue title prefixes (`[US]`, `[TASK]`, `[BUG]`).
   - Logs Agile state transitions to `$GITHUB_STEP_SUMMARY` and syncs new items to the Project Board.

> **[INSERT SCREENSHOT 2: GitHub Project Workflows Settings page showing enabled automation rules]**
>
> **[INSERT SCREENSHOT 3: GitHub Actions tab showing `Agile Board & Workflow Automation` and `CI` workflows]**

---

## 4. User Stories, Tasks & Sprint Tracking

### 4.1 Issue Form Templates
Standardized YAML issue forms were created in `.github/ISSUE_TEMPLATE/`:
- `user_story.yml`: Captures *"As a / I want / So that"*, Acceptance Criteria, Story Points, Priority, and Target Sprint.
- `task.yml`: Captures technical sub-tasks linked to parent User Stories.
- `bug_report.yml`: Captures CI regressions and defect severity.

> **[INSERT SCREENSHOT 4: GitHub Issues "New Issue" page displaying User Story, Technical Task, and Bug Report templates]**

### 4.2 Sprint Breakdown & Backlog

#### Sprint 1: Core E-Commerce & Baseline CI (Completed)
| Type | Title | Story Points | Priority | Status |
| :--- | :--- | :---: | :---: | :--- |
| User Story | `[US] Implement Pricing & Discount Engine` | 3 | High | Done |
| User Story | `[US] Implement Shopping Cart & Inventory Management` | 5 | High | Done |
| User Story | `[US] Configure Baseline CI Pipeline with Pytest` | 3 | High | Done |
| Task | `[TASK] Set up Python 3.12 virtual environment and pytest.ini` | 1 | Medium | Done |

#### Sprint 2: Smart Build-Cache, Test Routing & ML Prediction (Active)
| Type | Title | Story Points | Priority | Status |
| :--- | :--- | :---: | :---: | :--- |
| User Story | `[US] Smart Build-Cache Invalidation via Dependency Graph` | 5 | High | Done |
| User Story | `[US] Dynamic Test-Subset Routing for Faster CI` | 5 | High | Done |
| User Story | `[US] LLM-Based Build & Error-Log Summarization` | 3 | Medium | In Review |
| User Story | `[US] ML-Based Build-Failure Prediction (Warn-Only)` | 8 | Medium | In Progress |
| Task | `[TASK] Generate synthetic CI history & train Random Forest model` | 3 | Medium | Done |
| Bug | `[BUG] Handle empty git diff fallback in select_tests.py` | 2 | High | Todo |

#### Sprint 3: Future Enhancements (Backlog)
| Type | Title | Story Points | Priority | Status |
| :--- | :--- | :---: | :---: | :--- |
| User Story | `[US] Slack / Discord Notifications for Predicted Build Failures` | 3 | Low | Backlog |
| User Story | `[US] Automated Sprint Velocity & CI Health Dashboard` | 5 | Low | Backlog |

> **[INSERT SCREENSHOT 5: GitHub Issues List & Milestones page showing Sprint 1 and Sprint 2 progress bars]**
>
> **[INSERT SCREENSHOT 6: Detailed view of an opened User Story issue showing Acceptance Criteria, Labels, Milestone, and Story Points]**

---

## 5. Screenshots of Work Done

*(Replace the placeholders in Sections 3 and 4 or attach all 6 screenshots below before exporting to PDF/DOCX for submission.)*

1. **Screenshot 1:** `SmartCI Agile Sprint Board` (Kanban Board View with cards across columns)
2. **Screenshot 2:** `Project Workflows` configuration screen (Auto-close, PR merged, Auto-add rules)
3. **Screenshot 3:** `GitHub Actions` workflow runs (`Agile Board & Workflow Automation` + `CI`)
4. **Screenshot 4:** `New Issue` template chooser (`User Story`, `Technical Task`, `Bug Report`)
5. **Screenshot 5:** `Milestones` view (`Sprint 1` 100% complete, `Sprint 2` in progress)
6. **Screenshot 6:** Individual `[US]` User Story issue detail view with labels, milestone, and Project sidebar

---

## 6. Personal Observations & Learnings

1. **Tight Code-to-Board Traceability:** Unlike standalone tools (such as Trello or Miro), GitHub Projects links User Stories directly to commits, branches, Pull Requests, and CI runs (`ci.yml`). Using `Closes #<issue>` in a PR automatically moves the card to `Done` upon merge.
2. **Structured Requirements via Issue Forms:** Defining `.github/ISSUE_TEMPLATE/user_story.yml` enforced consistent *"As a / I want / So that"* formatting and explicit Acceptance Criteria before any implementation began.
3. **Automation Reduces Manual Overhead:** Combining GitHub Projects' built-in workflows with `.github/workflows/agile-board-sync.yml` eliminated manual card-dragging and label-tagging.
4. **Sprint Planning & Estimation:** Using Fibonacci Story Points (`1, 2, 3, 5, 8`) and Milestones made it easy to separate completed foundational work (Sprint 1) from active SmartCI ML features (Sprint 2) and future ideas (Sprint 3 Backlog).
5. **Limitations Observed:** GitHub Projects v2 does not generate traditional Scrum burndown charts out-of-the-box on free personal repositories without upgrading to GitHub Team/Enterprise insights, whereas tools like Jira provide built-in velocity and burndown charts natively.
