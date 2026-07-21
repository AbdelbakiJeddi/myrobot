# myrobot — General Working Rules

> Kanban: ClickUp. Read this file first.
> Need to create a task? Copy `NEW_TASK_TEMPLATE.md`.
> Task finished? Copy `TASK_DONE_TEMPLATE.md` into the PR body.

---

## 1. Ground Rules

1. One task = one PR.
2. One PR = one branch. Branch name = task ID slug.
3. No direct push to `main`. Always via PR.
4. CI must be green before review.
5. At least 1 approval before merge.
6. Close task only when PR merged AND verified.
7. Ask before touching someone else's task.

---

## 2. Task Workflow (ClickUp)

Statuses flow left to right:

```
Backlog → To Do → In Progress → In Review → Verify → Done
```

| Status | Meaning |
|---|---|
| Backlog | Captured, not refined. |
| To Do | Ready to claim. Has all fields from template. |
| In Progress | Branch created, work active. |
| In Review | PR opened, CI green. |
| Verify | PR merged. Needs run on rig/sim. |
| Done | Verified. Closed. |
| Blocked | Stuck > 1 day. Comment why. |

---

## 3. Task Anatomy

Every task must have these fields (from `NEW_TASK_TEMPLATE.md`):

- **Title** — verb-led, ≤ 80 chars.
- **Description** — what, why, short.
- **Desired Output** — success looks like (files, behavior, demo).
- **Input** — data, topics, files, dependencies.
- **Configuration** — params, env vars, ROS topics, launch args, thresholds.
- **Docs Needed** — docs to write or update.
- **Type label** — `bug`, `feature`, `chore`, `docs`, `hw-firmware`, `sim`, `refactor`.
- **Area label** — `area:control`, `area:hardware`, `area:localization`, etc.
- **Priority** — `P0` / `P1` / `P2` / `P3`.
- **Assignee** — one person.
- **Branch link** — set when work starts.
- **PR link** — set when PR opens.

All fields written before any code.

---

## 4. Branch & Commit

**Branch:**
```
type/CU-id-kebab-slug
```

**Commit (Conventional Commits):**
```
type(scope): subject  (CU-abc123)

body — write WHY, not what

Closes CU-abc123
```

---

## 5. PR Rules

- Title = commit subject.
- Body filled from `TASK_DONE_TEMPLATE.md` (short desc, what did, data, input, output, changes, packages, how to run, args).
- Always include `Closes CU-abc123` in body.
- Draft until CI green.
- 1+ review approval before merge.
- No force-push after first review.

---

## 6. Tunings

Any change to PID, EKF, navigator gains: document in the PR description what changed, old vs new value, why, and link the test run.

No silent retunes. Ever.

---

## 7. Quick Checklist

- [ ] Task in ClickUp before code, using `NEW_TASK_TEMPLATE.md`
- [ ] All fields filled (desc, output, input, config, docs)
- [ ] Branch = `type/CU-id-slug`
- [ ] Commits conventional, reference `CU-abc123`
- [ ] PR body filled from `TASK_DONE_TEMPLATE.md`
- [ ] CI green before review
- [ ] 1+ approval
- [ ] Run on rig/sim, linked in PR
- [ ] Tuning changes documented in PR if applicable
- [ ] ClickUp task moved to `Done` only after merge + verify
