# Codex Workspace: Robotics Code Work Lane

**Read order for any Codex session (the harness, added Nov 11, 2026):** `AGENTS.md` first (roles, First and Last Mile, work ethic, stop conditions), then `CONTEXT.md` (standing context, goals, research, silhouettes, known unknowns), then `HARNESS.md` (folder structure and file info), then `OPEN_LOOPS.md` (this lane's registry), then the packet. This README holds the setup state and packet format underneath that layer. No task instructions go through until Thunder approves the harness.

Prepared Nov 10, 2026. Status: **set up to the login wall.** Codex CLI 0.164.0-alpha.9 is installed on this VM and configured (`~/.codex/config.toml`), packets and run directories are staged, and no Codex run has happened. Nothing here touches the delivered claw series or Drive.

**Thunder's one step: run `codex login` on this VM and finish the ChatGPT sign-in it opens; everything else is already set up.**

## Layout

```text
~/workspace/robotics-fresh/codex/
  README.md            this file: layout, packet format, run procedure
  packets/             one Markdown file per packet; a packet file is the
                       complete, self-contained prompt for a Codex run
  runs/<packet-id>/
    input/             staged copies of the base files, hash-pinned in the
                       packet; Codex reads these, never the originals
    work/              Codex's scratch space for the run
    output/            candidate files Codex produces (new versioned
                       names, never edits in place)
    report/            Codex's validation report: raw check outputs and
                       the exact diff, written by the run itself
```

## How a run works

1. A packet is written under `packets/` and its run directory is staged with hash-pinned inputs.
2. After login exists, the Robotics Code Work chat fires the run non-interactively from the run directory: `codex exec` with the packet file as the prompt, sandbox limited to the run directory (config posture: workspace-write, approvals on-request).
3. Codex returns candidate files in `output/` and its validation report in `report/`. Codex output is a candidate, never a delivery.
4. This chat verifies the report against the acceptance proof named in the packet, then the normal workflow resumes: verified candidates go to Thunder first, and only his gates move anything to Drive or a new version line.

## Packet format (spec in, patch plus validation report out)

Every packet file carries, in this order:

- **Packet ID and status** (ready, blocked-on, done).
- **Objective:** one change, stated as behavior, in Thunder's words where he gave them.
- **Base:** exact input files with SHA-256 hashes, staged under the run directory's `input/`.
- **Spec:** the named constants, functions, and values or behavior to change. Nothing implied, nothing left to interpretation.
- **Acceptance proof, named up front:** the exact checks that decide pass or fail, including the expected diff shape (which lines may change, which files may be created).
- **Boundaries and blast radius:** files it may touch, files it may not, scratch-only or delivery-eligible.
- **Guardrails:** the block below, verbatim.
- **Handback:** candidate files in `output/`, a validation report in `report/` containing raw outputs (parse results, device and definition counts, the full unified diff against base), a label list for any new or changed tune variable, and open questions stated plainly.

The validation standard inside every packet is this chat's fixed standard: ast.parse on both files, no duplicate top-level defs, exactly one `imu = Inertial`, exactly one `#endregion`, robotConfig device count checked (11 on the current wiring), and a line diff against the base reviewed so the result is exactly the ordered change and nothing else. For PROS (C++) work the same standard translates: clean build or syntax check with the toolchain state stated honestly, device map diffed port by port against the Python source of truth, and the same exact-diff discipline per step.

## Guardrails (verbatim in every packet and artifact in this lane)

- Per-motor factors are scales, not caps.
- Drive torque stays at 100; slowing is done by speed alone, never by cutting torque.
- Every new tune variable is labeled UNTESTED or MATH-VERIFIED with its dependencies named, and is treated as wrong until it is manually tested, tuned, and confirmed on hardware, or it is mathematically correct with everything it relies on verified.
- No claim about drive direction, snap turns, or heading hold until the by-hand IMU heading check and the wheels-up test pass.
- The PROS switch is undecided; no run assumes PROS unless Thunder's packet says so.
- Codex never chooses values, never decides version numbers or pushes, never makes a hardware claim, and never contacts Thunder directly.
- v17, v18, and Drive are untouched by any setup or prep work in this lane.
