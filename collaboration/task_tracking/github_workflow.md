# Git & GitHub Collaboration Workflow

## 1. Branching Strategy
- `main`: Always clean, tested, and reproducible. Direct pushes to `main` are discouraged once team collaboration begins.
- Feature branches: `feat/<task-id>-<short-topic>` (e.g., `feat/T06-scenarios-s01-s04`, `eval/T11-pgbadger-report`).

## 2. Pull Request & Peer Review Rules
1. Pull latest `main` before branching:
   ```powershell
   git checkout main
   git pull origin main
   git checkout -b feat/T06-scenarios-s01-s04
   ```
2. Never stage or commit secrets or runtime data (`.env`, `pgdata/`, `logs/`). Check `git status` before committing.
3. Open a Pull Request targeting `main` using `.github/pull_request_template.md`.
4. **Mandatory Cross-Review:** At least one teammate (not the author) must pull the branch, test the SQL/script or verify the evaluation artifact, and approve the PR before merging.

## 3. Creating GitHub Issues from Backlog
Import or create issues from `collaboration/task_tracking/github_issues_backlog.csv` using `.github/ISSUE_TEMPLATE/task_issue.md`, assigning each to `P1`, `P2`, or `P3` (mapped to Mrida, Atika, Jasnav).
