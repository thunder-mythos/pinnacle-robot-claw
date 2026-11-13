# PROCEDURE.md — How a Codex packet runs

One packet, end to end. This is the procedure every Codex run follows, pilot or real work.

## Roles (short version)

- Thunder: first mile (intent) and last mile (proof, final physical steps), every gate.
- Corvin: orchestration. Writes packets, dispatches, verifies the log and the diff, delivers. Corvin never reads code. That separation is the point: if Corvin keeps reading code, the spend just moves to Codex input tokens and doubles.
- Codex: the middle. Executes packets exactly, reads and writes code in its own cloud env, logs every action, returns candidates plus proof.

## The nine steps

1. Packet (Corvin). Objective, exact base (repo commit), change spec, acceptance proof named up front, boundaries and blast radius, guardrails verbatim, model and effort. Written from intent and spec. No code reading to write it.
2. Dispatch (Corvin, CLI). `codex cloud exec --env <id> --branch main -c model="<model>" -c model_reasoning_effort="<effort>" "<packet prompt>"`. The 5-hour window is checked against the 90% hard line before every dispatch. Thunder watches in his ChatGPT app.
3. Startup (Codex). Reads AGENTS.md, CONTEXT.md, HARNESS.md, PROCEDURE.md, OPEN_LOOPS.md, then the packet. Confirms the base in its env. Opens the run log.
4. Work (Codex). Only the specified change, inside the envelope. Runs the fixed validation standard as it goes. Every new or changed tune variable gets labeled UNTESTED or MATH-VERIFIED with dependencies named. Every action goes in the log.
5. Stop (Codex). Stops instead of guessing on: base mismatch, ambiguous or incomplete spec, spec contradicts a guardrail, task touches drive direction, snap turns, or heading hold, a value nobody gave, or anything outside the envelope (Drive, pushing, contacting a person). Writes the question and stops.
6. Handback (Codex). Candidate files, exact unified diff, raw validation output, label list, open questions, and the run log. In cloud form: task diff on branch `codex/<packet-id>-<slug>`, PR titled `[<packet-id>] <objective>`. The log is committed on the branch with the rest.
7. Re-ping (Codex). Last action: ping the ordering chat with packet id, status, deliverable path, one line summary, blocker or question.
8. Verify (Corvin). Reads the run log and reviews the diff, checks the validation output. No hashes, no byte sizes. A human dev reads the log and the diff; Corvin does the same. The loop in OPEN_LOOPS.md closes only on that proof.
9. Deliver (Corvin). Finished result only, plus any decision that is Thunder's: values, push, hardware claims, the PROS switch.

## The run log

Everything an agent does gets logged in one hierarchical markdown file per run. This is the audit trail. It is how a wrong spec gets caught: the log shows what the agent actually did, step by step, and the log plus the diff is what gets reviewed.

### File

- One log per run: `codex/runs/<packet-id>/LOG.md`.
- Lives in the cloud env during the run, local to the agent. Pushed to GitHub with the handback at the end of the run.
- The end of a run is when the work is done and handed back, or when something is being passed between agents. Handoffs between agents are rare, and Corvin keeps them that way.

### Frontmatter

Every log carries frontmatter. The agent reads the frontmatter only, never the full file again. That is what keeps appends cheap.

```yaml
---
packet: FLM-V2-PILOT-001
run: 1
model: gpt-6.1-terra
effort: medium
status: running
last_heading: "### Action 3 — Regenerate wrapper"
last_action: 3
---
```

- `status`: running, done, blocked, failed.
- `last_heading`: the exact heading text of the most recent entry. It tells the agent whether to append under the existing heading or start a new one.
- `last_action`: the number of the most recent action.

### Heading hierarchy (strict, follow closely)

- `# Run log — <packet-id>` — once, at the top.
- `## <phase>` — one per phase, in fixed order: Dispatch, Startup, Work, Validation, Handback.
- `### Action <n> — <verb> <target>` — one per action, numbered in order from 1.
- Body under each action, fixed bullets in this order:
  - `timestamp:` when it happened (CST).
  - `tools:` what was used.
  - `objective:` what this action was for.
  - `outcome:` what happened, done or failed or stopped, with the detail.
  - `notes:` only if needed (questions, blockers).

### Append rule

1. Read the frontmatter only.
2. If the next entry continues the same action, append its bullets under `last_heading`.
3. If it is a new action, append a new `### Action <n>` heading under the current `##` phase (new phase heading first if the phase changed), then update `last_heading` and `last_action` in the frontmatter.
4. Never read the full file to append. The frontmatter carries everything the append needs.

### What gets logged

Every action: reads, edits, validation runs, stops, questions, handback steps. Nothing unlogged. A gap in the log is a gap in the proof.

## Naming

Branches `codex/<packet-id>-<slug>`, PR titles `[<packet-id>] <objective>`. After the pilot passes, the naming scheme changes: the new PROS C++ generation gets its own naming, and claw_vN stays with the Python generation. That change is queued, not decided here.
