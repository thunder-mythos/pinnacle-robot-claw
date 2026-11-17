# Packet FLM-V2-PROS-LEMLIB-001: LemLib parity port of claw_v17

- **Status:** ready to fire Nov 17, 2026. One-way route: Thunder drives it in the web app.
- **Loop:** CX-12 (LemLib conversion track).
- **Model and effort:** GPT-6.1 Sol, Medium. Never Low. The 5-hour window never goes over 90%.
- **Route:** one-way. This packet is executed by Codex in a cloud task thread, driven by Thunder. The kit zip is attached to the thread; unpack it and use its files. Do not use the CLI dispatch route.

## Objective

Port claw_v17 (VEXcode Python, the current delivered version) to PROS C++ on LemLib, behavior parity only. The port does what v17 does, nothing more, nothing less. Slew limiting is the follow-up packet, not this one. No library-only capability is adopted beyond what parity needs. No odometry moves, no pose moves, no pure-pursuit paths in this port; those are later packets.

## Base (confirm before touching a file)

- **Source code:** `base/claw_v17.py` and `base/claw_v17.v5python` in the kit. Confirm they match the repo's `claw/claw_v17.py` and `claw/claw_v17.v5python` (diff them; a mismatch is a stop). v17 is 359 lines; DEFENSE_RETURN_VEL is 60.0.
- **Template:** `pros/pros-templates/lemlib/` in the kit. Copy it into `work/lemlib/` inside your run directory and port there. Do not edit the kit's copy in place. Read the template's own README.md in the copy; it carries a v17 feature map for this template. Follow `firmware/LIBRARY-NOTE.md` for applying LemLib (`pros c apply LemLib`; the binary goes in firmware/, nothing about it is checked in).
- **Reference, not base:** `pros/pros-scaffold/` (plain PROS mirror of v17), `pros/pros-transition-protocol.md` (adoption order and gates), `pros/pros-movement-research.md` (evidence base), `harness/FEATURE-COMPARISON.md` (the shared parity spec; this packet's verdicts come from it).
- **Startup ritual:** read `harness/AGENTS.md`, `harness/CONTEXT.md`, `harness/HARNESS.md`, `harness/PROCEDURE.md`, `harness/OPEN_LOOPS.md` in that order, then this packet in full.

## Change spec (parity, feature by feature)

Port all 20 v17 features. Verdict key: LIB (use the library's version), TEAM (stays team code), WRAP (library primitive wrapped by team code), DROP (deliberately not ported).

| # | Feature | Verdict in this track |
|---|---|---|
| 1 | Device map: 4 drive blue 6:1 (10, 9, 1 rev, 2 rev), 4 lift green 18:1 (7, 6, 4 rev, 5 rev), claw DigitalOut A, RearSpinner 21 (code kept, hardware removed), IMU 15 | LIB (MotorGroups, negative port = reversed) |
| 2 | Torque 100 on every motor, set once, never changed | LIB (current limit pinned once; motion via chassis or move_velocity) |
| 3 | Per-motor drive scales 100/100/80/80 | GAP, accept per-side scales (Thunder's Nov 11 ruling; v17's values are uniform within each side) |
| 4 | Drive direction in one place (DRIVE_SIGN -1.0) | TEAM (sign lives in team code; chassis has its own conventions) |
| 5 | Two-zone drive stick curve | DROP (Thunder's rule against stick shaping; restoring it is his call) |
| 6 | Turn stick linear, capped at 60% of mode cap | TEAM (turn input fed to the chassis) |
| 7 | Two modes: regular 30, Function 70 | TEAM (team state, applied before the chassis call) |
| 8 | Per-mode Up/Down adjustment, steps of 10, persist through match | TEAM |
| 9 | Heading hold (KP 1.0, max corr 20, tol 1 deg) | WRAP (team code feeding turn input from chassis.getPose().theta) |
| 10 | IMU snap turns +-90 deg, two-speed, stop inside 3 deg, brake landing, 1 s timeout | WRAP (turnToHeading with maxSpeed; LemLib PID + exit conditions replace the two-speed profile, equivalence UNVERIFIED) |
| 11 | Output smoothing overlay (currently off) | TEAM (smooth_step() before the chassis) |
| 12 | Coast at rest, brake only at IMU turn end, lift HOLD | LIB (the policy of where each applies is TEAM) |
| 13 | Lift 50%, HOLD, 64 deg/in | TEAM on library motor groups |
| 14 | Claw B toggle; startup closes it first | TEAM (mechanisms.cpp, first line of initialize()) |
| 15 | RearSpinner R1 held reverse 100% | TEAM (polled in the driver loop) |
| 16 | Defense mode: Y toggle, spin 90, return at 60 | WRAP (spin via chassis.arcade, return via turnToHeading) |
| 17 | Auton two-step: close, wait 500 ms, lift 1 in | TEAM (auton_v17_parity()); structural note: LemLib calibrates in initialize(), so v17's "auton does not wait for IMU" cannot be mirrored exactly |
| 18 | Auton building blocks | LIB (moveToPoint / moveToPose / follow with PID and exit conditions) |
| 19 | IMU calibration at startup | LIB (chassis.calibrate()) |
| 20 | Competition structure | LIB (initialize, autonomous, opcontrol) |

Settled values (do not re-decide): defense return is 60.0 (v17's value; v18's 40.0 is one config line, and v18 is unpushed). Per-motor values are applied as scales, never caps. DRIVE_SIGN is UNVERIFIED on the PROS side. Track width is a placeholder (11.5 in, MEASURE ME); flag it as an open question in your report, do not guess a value. No drive, snap, or heading claim stands until the by-hand IMU check (CX-08) and the wheels-up test (CX-09) pass; port the code, claim nothing about the robot.

## Acceptance proof (named up front, pass or fail)

- The ported project builds in the cloud environment against the real PROS kernel. The raw build log is kept in the report.
- Device map diffed port by port against v17: all 11 devices present with the same ports and reversals.
- Parity table complete: all 20 features present with the verdict applied, or explicitly marked not portable with the reason.
- Every new or changed tune variable is listed as UNTESTED or MATH-VERIFIED with its dependencies named. Unlabeled values fail the run.
- No hardware claim anywhere in the report. A clean build is not robot validation.
- The run log is complete per PROCEDURE.md, frontmatter status done, no gaps.
- Handback: the ported project on branch `codex/pros-lemlib-parity`, PR titled `[FLM-V2-PROS-LEMLIB-001] LemLib parity port of v17`, plus `report/validation.md` (build log, device map diff, parity table, label list, open questions) and `LOG.md`. Merge is Thunder's gate. If the push fails, hand back the project tree as files in the thread and report the failure plainly instead of failing silently.

## Boundaries

- Work only inside `codex/runs/FLM-V2-PROS-LEMLIB-001/` in this checkout. The template copy you port is `work/lemlib/`; the kit's files are not the working surface.
- No Drive. No contacting any person. No touching `docs/`. No touching the Python claw series (v17, v18, Drive).
- No improving beyond parity: no slew (follow-up packet), no odometry or pose moves, no pure-pursuit paths, no library-only capability beyond what a row above needs.
- No cross-merging with the EZ-Template track. It runs in its own thread on its own branch. If the two tracks disagree on a shared question, write it in your report; do not resolve it by editing the other track.
- Stop and write the question if the spec is ambiguous, the base does not match, a value nobody gave is needed, or the work would reach outside this envelope.

## Run directory

`codex/runs/FLM-V2-PROS-LEMLIB-001/` in the checkout at `/workspace/pinnacle-robot-claw`: `input/` (staged base + template copy), `work/` (the port in progress), `output/` (the finished project tree), `report/` (validation.md with raw outputs). `LOG.md` at the run root per PROCEDURE.md.
