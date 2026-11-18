# RBC-Map Multi-Agent Development Plan

Status: Proposed; manual pilot before automation.
Owner/final approver: Repository maintainer.
Source of truth: GitHub issues, branches, commits, PRs, checks and audit records.

## Objective
Deliver small, testable RBC-Map changes using independent implementation, audit, validation/remediation and PR review. Prevent AI agents from approving their own work or merging autonomously.

## Responsibilities
| Stage | Agent | Deliverable | Boundaries |
| --- | --- | --- | --- |
| 0. Scope | Maintainer | GitHub issue with acceptance criteria, constraints and risk | Authorizes work |
| 1. Implement | Codex | Feature branch, code, tests, implementation handoff | No direct merge |
| 2. Audit | Claude Code | Evidence-based audit report, without modifying implementation | Independently assess code, tests, security and architecture |
| 3. Validate/remediate | Devin | Reproduced findings, accepted/rejected dispositions, targeted fixes, regression evidence | Do not blindly implement audit suggestions |
| 4. Review | Greptile | PR review findings | Independent reviewer; may miss defects |
| 5. Gate | CI + maintainer | Passing checks and explicit merge decision | Only maintainer merges |

## Workflow
1. Maintainer opens an issue with objective, acceptance criteria, affected paths, exclusions, and rollback instructions.
2. Codex creates a branch from the agreed base (normally `dev` for ongoing development; confirm target before starting), implements the smallest coherent change, and records tests and assumptions.
3. Claude Code reviews the exact commit SHA and publishes findings in `.agents/handoffs/` or the PR. Each finding must include ID, severity, file/line, evidence, reproduction/impact and suggested correction. No speculative finding is labeled confirmed.
4. Devin independently verifies each finding. Record `confirmed`, `false_positive`, `needs_information`, or `accepted_risk` with evidence. Fix confirmed findings on the feature branch or a dedicated remediation branch, add regression tests, and document all changes.
5. Open or update a PR to the agreed target branch. Greptile reviews the final diff. Confirm that its review actually ran; no comments is not proof of correctness.
6. If Greptile finds issues, route actionable findings back to Devin, request Claude re-audit of material changes, rerun CI, and obtain a fresh Greptile review where supported.
7. Maintainer reviews the PR, unresolved findings and checks; merges or rejects. No autonomous merge.

## Gates and failure policy
- Require Python syntax compilation, linting, tests, and any applicable security checks. Syntax compilation should cover changed Python files and the active project tree; do not assume a removed or historical `testing/` tree exists.
- Treat failed or missing CI as a block, not as a pass. If GitHub Actions is billing-blocked, run equivalent checks locally and record logs, but do not describe CI as green.
- Block unresolved critical/high findings unless maintainer explicitly documents a risk exception. Medium/low findings must be tracked or resolved.
- Maximum two automatic remediation/re-review cycles per PR. Escalate unresolved or conflicting findings to maintainer.
- Avoid simultaneous agent writes to the same branch. Pin handoffs to commit SHA; re-audit after material code changes.
- Never expose secrets, tokens, local credential databases, or private user data to prompts, logs or PRs.
- Restrict GitHub/App permissions to least privilege and review costs before enabling unattended agents.
- Keep releases and versioned archives unchanged unless the issue explicitly authorizes edits.

## RBC-Map pilot
1. Establish baseline checks on the active development branch; ensure tests do not depend on live game services or real credentials.
2. Use a small, reversible issue affecting the active development tree; run Codex -> Claude -> Devin -> Greptile manually.
3. Evaluate true positives, false positives, missed bugs, time, cost, code churn, test quality, and handoff clarity.
4. Repeat on a meaningful logic/regression test, not only a syntax typo.
5. Automate handoffs only after successful manual trials and explicit maintainer approval.

## Known review experiment
PR #16 (`test/greptile-unicode-syntax`) introduced U+037E after a Python statement in `testing/main_0.14.0.py`. The reported Greptile Base review completed without flagging the deliberate syntax error. This is a single observed miss, not a comprehensive benchmark. Keep intentional-defect PRs unmerged; verify reviewer configuration before drawing broader conclusions.

## Future automation (not enabled by this plan)
Use GitHub issue/PR labels and protected environments or approval gates to trigger agents sequentially. Require human approval for agent writes, billing-sensitive jobs, and merge. Use unique correlation IDs for each issue/PR/handoff and preserve full logs.
