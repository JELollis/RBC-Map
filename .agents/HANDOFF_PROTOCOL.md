# Agent Handoff Protocol

Every handoff must identify repository `JELollis/RBC-Map`, issue/PR number, source and target branch, exact commit SHA, owner, timestamp, scope and status. Put records in `.agents/handoffs/` or PR comments; do not store credentials.

## Common handoff template
```markdown
# Handoff: <issue>-<stage>
Stage: codex-implementation | claude-audit | devin-validation | greptile-review
Repository: JELollis/RBC-Map
Issue / PR:
Source branch:
Target branch:
Reviewed commit SHA:
Owner:
Status: ready | blocked | changes-requested | accepted
Scope and acceptance criteria:
Changed files:
Commands executed and results:
Unexecuted checks and reason:
Risks / assumptions:
Artifacts / links:
Next owner and requested action:
```

## Claude finding template
```markdown
ID: AUD-001
Severity: critical | high | medium | low | informational
Confidence: high | medium | low
Location: path:line (commit SHA)
Claim:
Evidence / reproduction:
Expected vs actual:
Impact:
Recommended fix:
Status: unverified
```

## Devin disposition template
```markdown
Finding ID:
Disposition: confirmed | false_positive | needs_information | accepted_risk
Verification steps and result:
Fix commit(s), if any:
Regression test and result:
Remaining risk:
```

## Greptile review handoff
Record review URL, review mode, reviewed head SHA, completion state, all actionable comments and whether re-review is needed. An empty review is not a pass. Greptile comments must be independently verified before edits.

## Stop conditions
Stop and request maintainer approval for destructive changes, secret handling, data migrations, dependency/permission changes, release changes, ambiguous requirements, conflicting audit conclusions, missing tests, or more than two remediation loops.
