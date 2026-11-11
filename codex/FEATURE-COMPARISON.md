# Feature Comparison: Our Code vs the PROS Libraries

- **Date:** Nov 11, 2026
- **Method (Thunder's, Nov 11):** list every feature in our current code, list every feature each PROS library/template provides, compare the two lists, and wherever a library wins, use the library. The assumption is that the prebuilt work of people better at this than us beats our from-scratch work. The port is written as if the code had been made in that library from the beginning.
- **Source of truth, our side:** claw_v17.py, read in full Nov 11, 2026 (359 lines). Every feature below traces to it.
- **Source of truth, library side:** the three template trees under `~/workspace/robotics-fresh/pros-templates/` (each with its own README containing a v17 feature map, read Nov 11, 2026) plus `~/workspace/robotics-fresh/pros-movement-research.md` (Nov 7). Library API names are UNVERIFIED against installed headers: no PROS toolchain exists on this VM and nothing here has compiled. First build in the cloud environment settles name drift.
- **Status:** comparison only. No conversion packet has fired. The PROS switch itself is still undecided.

## Dispatch standard for this phase (model and effort)

Thunder asked where I stand on model and effort before the first build. Here it is, per task, set in each packet:

- **Model:** Codex's current default is GPT-6 Sol, the model OpenAI recommends for complex coding and agentic work; GPT-6 Luna is the lighter model for focused, repeatable tasks. The CLI sets the model per dispatch with `-m` (verified in the installed CLI's help). My stance: the pilot (a mechanical one-line reproduction with an exact hash proof) runs on **Luna**, because thinking harder buys nothing there; the conversion work runs on **Sol**, because it is design-heavy and the cost of a wrong port is a broken build and a wasted cycle. The account's available models are the final authority; if Sol is not on his plan, the packet says so and falls back to the strongest available.
- **Effort:** reasoning effort is a per-task config setting (low, medium, high), applied through the config override the CLI supports. My stance: pilot runs **low** effort, conversion packets run **high** effort. Effort is recorded in each packet so every task carries its own spend. One honest caveat: the effort key name comes from Codex documentation, not from this CLI's help text; I confirm the accepted values on the first dispatch and correct this record if it differs.
- **Cost note:** every Codex run draws on his ChatGPT plan allowance, shared across Codex seats. Low effort on mechanical tasks is how the allowance is protected.

## Our feature list (claw_v17)

| # | Feature | Where in v17 |
|---|---|---|
| 1 | Device map: 4 drive blue 6:1 (ports 10, 9, 1 rev, 2 rev), 4 lift green 18:1 (7, 6, 4 rev, 5 rev), claw DigitalOut A, RearSpinner port 21 (code kept, hardware removed), IMU port 15 | Top of file, devices |
| 2 | Torque 100 on every motor, set once in startup, never changed after | `startup()` |
| 3 | Per-motor drive scales 100/100/80/80 (left/right) | `set_drive()` clamps |
| 4 | Drive direction handled in one place: DRIVE_SIGN -1.0 inside `set_drive()` | `set_drive()` |
| 5 | Two-zone drive stick curve: deadband 5%, 0-50% over first 85% of stick, 50-100% over last 15% | `drive_map()`, KNEE_STICK 0.85, KNEE_VEL 50 |
| 6 | Turn stick linear with deadband, capped at 60% of the active mode cap | `turn_map()`, TURN_RATIO 0.6 |
| 7 | Two drive modes: regular starts 30, Function (R2 held) starts 70, each its own cap | `driver_loop()`, DRIVE_START_REG/FN |
| 8 | Per-mode speed adjustment: Up/Down steps of 10 within 10-100, separate per mode, persists through match, resets on restart | `on_up()`, `on_down()` |
| 9 | Heading hold: while driving with no turn input, hold captured heading with P correction (KP 1.0, max corr 20, tol 1 deg) | `driver_loop()` |
| 10 | IMU snap turns: Fn+Left/Right +-90 deg, two-speed (60 far, 25 inside 15 deg), stop inside 3 deg, brake landing, 1 s timeout failsafe | `imu_turn()`, `on_left()`, `on_right()` |
| 11 | Output smoothing overlay (SMOOTH_TAU; currently 0, effectively off) | `driver_loop()`, `k` factor |
| 12 | Coast at rest for drive, brake only at the end of IMU turns, lift HOLD at rest | `stop_drive()`, `imu_turn()` end, `startup()` |
| 13 | Lift: L1/L2 buttons up/down at 50%, HOLD at rest, lift measured in inches (64 deg/in) | `lift_inches()`, driver loop |
| 14 | Claw: B toggle through one set function; startup closes it first, before motor setup and IMU calibration | `claw_set()`, `claw_close()`, `startup()` |
| 15 | RearSpinner: R1 held gives 100% reverse | driver loop, defense branch |
| 16 | Defense mode: Y toggle, captures heading, spins in place at 90%, lift and spinner stay live, toggle off returns to captured heading at 60 | `on_y()`, defense branches |
| 17 | Auton: close claw, wait 500 ms, raise lift 1 inch, stop | `run_autonomous()` |
| 18 | Auton building blocks: encoder drive in inches at 0.65 of driver values, IMU turn at 0.65 x TURN_MAX | `auton_drive_inches()`, `auton_turn_deg()` |
| 19 | IMU calibration at startup (~2 s, robot still), imu_ready flag, driver loop waits for it | `calibrate_imu()`, `wait_for_imu()` |
| 20 | Competition structure: autonomous and driver threads, button callbacks (B, Y, Up, Down, Left, Right) | `autonomous()`, `user_control()`, bottom of file |

## What each library provides

### LemLib

- Odometry and pose tracking: chassis tracks x, y, heading; `moveToPoint`, `moveToPose`, `turnToPoint`, `turnToHeading`, pure-pursuit `follow` on drawn path files (assets in `static/`).
- PID motion with exit conditions: lateral and angular `ControllerSettings` with small and large error timeouts and slew, replacing two-speed turn profiles and dead-reckoned drives.
- `ExpoDriveCurve` stick curves, `Drivetrain` and `OdomSensors` configuration, `chassis.calibrate()`.
- Costs: heaviest dependency, releases pin specific PROS 4.x kernels, a v0.6 rewrite is in progress upstream so the API may shift mid-season, steepest learning curve, PID tuning is a hardware project, track width is a placeholder (11.5 in, MEASURE ME).

### EZ-Template

- `ez::Drive` chassis from port lists, IMU port, wheel diameter and RPM; `pid_drive_set`, `pid_turn_set`, `pid_wait` motions with tuned-by-formula PID.
- Slew built in: the `slew_*_constants_set` family ramps auton motions natively.
- Exit conditions and chaining: motions end on measured settle behavior and chain into the next motion.
- Auton selector on the brain screen (`ez::as::AutonSelector`), so routines are chosen at the field instead of by recompiling.
- Built-in opcontrol schemes (tank, arcade standard, arcade flipped), driver curve and active brake configuration.
- No odometry, no pose. Path following and pose correction are not its ground.
- Structural cost: its built-in opcontrol owns the sticks and applies its own input curve, so our modes, snap, and defense live in a parallel team loop (`driver_features.cpp`) while EZ's driver assists stay out of the path.

### OkapiLib (legacy)

- `ChassisControllerBuilder` with `.withMotors`, `.withDimensions` (unit literals like `3.25_in`), `.withGains`, `.withOdometry`, `.buildOdometry()`.
- Unit-ful blocking motions (`moveDistance(24_in)`, `turnAngle(90_deg)`) and an async trapezoidal motion profiler for paths.
- `SkidSteerModel::arcade` consuming normalized -1..1 throttle and turn; applies no stick curve of its own.
- **Library status: archived upstream Jun 15, 2023, no maintenance.** Whatever build is applied is a frozen snapshot; kernel upgrades can break it with nobody obligated to fix it. This risk is written into the variant and stays written into any plan that uses it.
- No pure pursuit, no pose tracking of LemLib's class, no active slew tooling for driver input (the profiler smooths auton paths, not the stick).

### Plain PROS (the scaffold, for reference)

- No library features. Fast compiled C++ runtime, motor groups, direct voltage control, IMU and encoder access. Everything is hand-rolled. It is the baseline the three libraries are measured against, not a fourth contestant.

## The comparison: feature by feature, verdict per library

Verdict key: **LIB** means the library provides it and we use the library's version. **TEAM** means no library provides it and it stays team code. **WRAP** means the library provides the primitive and team code wraps it to get the behavior. **GAP** means no library provides it and no clean path exists. **DROP** means deliberately not ported, by Thunder's rule.

| # | Feature | LemLib | EZ-Template | OkapiLib |
|---|---|---|---|---|
| 1 | Device map | LIB (MotorGroups, negative port = reversed) | LIB (constructor lists, negative = reversed) | LIB (`.withMotors`, gearset in `.withDimensions`) |
| 2 | Torque 100, velocity-only | LIB (current limit pinned once; motion via chassis or `move_velocity`) | LIB with a flag (drive side is EZ's; its current behavior is library-defined, UNVERIFIED) | LIB (model commands velocity) |
| 3 | Per-motor scales 100/100/80/80 | GAP: per-SIDE scale only; per-motor inside a side has no path through a group-commanding chassis | GAP: same, per-side only | GAP: same; `arcade()` mixes sides internally, so even per-side scaling needs model wiring at first tuning |
| 4 | Drive direction in one place | TEAM (sign lives in team code; chassis has its own conventions) | TEAM | TEAM |
| 5 | Two-zone drive stick curve | DROP in all three, on guardrail grounds (it is stick shaping); restoring it is Thunder's call. Note: LemLib and EZ both ship their own curves, set to linear here for the same reason | DROP | DROP |
| 6 | Turn stick linear, capped | TEAM (turn input fed to the chassis) | TEAM | TEAM |
| 7 | Modes 30/70 + per-mode Up/Down | TEAM (team state, applied before the chassis call) | TEAM (team state in `driver_features.cpp`, not in EZ stock opcontrol) | TEAM (team state, most direct port of the three) |
| 8 | Per-mode adjustment, steps of 10, persist | TEAM (same as 7) | TEAM | TEAM |
| 9 | Heading hold | WRAP (team code feeding turn input from `chassis.getPose().theta`) | WRAP (team loop, heading from the chassis IMU getter) | WRAP (hand-rolled on `pros::Imu`; Okapi odometry heading is encoder-based) |
| 10 | Snap turns +-90 deg, 1 s cap | WRAP (`turnToHeading` with maxSpeed; LemLib PID + exit conditions replace the two-speed profile, equivalence UNVERIFIED) | WRAP (`pid_turn_set` inside an elapsed-time cap; EZ exit conditions are not a wall-clock cap, so the 1 s guarantee is team code, UNVERIFIED) | WRAP (hand-rolled two-speed IMU turn, plain-scaffold style; `turnAngle` deliberately unused) |
| 11 | Output smoothing (tau lag, currently off) | TEAM (`smooth_step()` before the chassis) | TEAM (team loop only; EZ curve set to 0) | TEAM (team code; Okapi adds no shaping) |
| 12 | Coast at rest / brake at turn end / lift HOLD | LIB (brake modes from the library; the policy of where each applies is TEAM) | LIB (same) | LIB (same) |
| 13 | Lift 50%, HOLD, 64 deg/in | TEAM on library motor groups | TEAM | TEAM |
| 14 | Claw B toggle, startup close first | TEAM (`mechanisms.cpp`, first line of `initialize()`) | TEAM | TEAM |
| 15 | RearSpinner R1 held reverse | TEAM (polled in the driver loop) | TEAM (team loop only; not in EZ stock opcontrol) | TEAM |
| 16 | Defense mode (spin 90, return at 60) | WRAP (spin via `chassis.arcade`, return via `turnToHeading`) | WRAP (spin in team loop, return via `pid_turn_set`) | WRAP (spin via model, proportional IMU return) |
| 17 | Auton two-step | TEAM (`auton_v17_parity()`); structural note: LemLib calibrates in `initialize()`, so v17's "auton does not wait for IMU" cannot be mirrored exactly | TEAM, plus LIB bonus: registered with the AutonSelector | TEAM |
| 18 | Auton building blocks (encoder drive, IMU turn) | LIB, big win: `moveToPoint` / `moveToPose` / `follow` with PID and exit conditions | LIB, big win: `pid_drive_set` / `pid_turn_set` with slew, exit conditions, chaining | LIB: `moveDistance` / `turnAngle` with units, plus motion profiler |
| 19 | IMU calibration at startup | LIB (`chassis.calibrate()`) | LIB (calibrates in `initialize()`) | TEAM (hand-rolled) |
| 20 | Competition structure | LIB (PROS lifecycle: `initialize`, `autonomous`, `opcontrol`) | LIB | LIB |

## New capabilities the libraries add (not in our code today)

| Capability | LemLib | EZ-Template | OkapiLib |
|---|---|---|---|
| Odometry and pose tracking | Yes | No | Encoder-only, no IMU fusion |
| moveToPose / pure pursuit paths | Yes | No | No |
| Motion chaining with exit conditions | Yes | Yes | Profiler paths only |
| Auton selector on the brain screen | No | Yes | No |
| Native slew on auton motions | Yes (controller settings) | Yes (slew constants) | Profiler smoothing only |
| Expo stick curves | Yes, set LINEAR by our rule | Yes, set 0 by our rule | No |
| Active brake on stick release | No | Yes | No |

## The porting rule (what the comparison decides)

1. Where a library provides the feature, use the library's version. That is the whole point: rows 1, 2, 12, 18, 19, and 20 are library wins in at least one template, and row 18 (auton motion) is the biggest single win in the entire comparison.
2. Where a library provides the primitive but not the behavior, team code wraps the primitive. Rows 9, 10, and 16 are wraps in all three libraries.
3. Where no library provides it, it stays team code, written in the library's idiom. Rows 4, 6, 7, 8, 11, 13, 14, and 15 are team code in every template.
4. The one structural gap: **per-motor scales inside a side (row 3) have no path in any library.** All three chassis models command motor groups, so a tune that splits L1 from L2 cannot pass through. Options, in order: (a) accept per-side scales, since v17's values are uniform within each side anyway; (b) build a custom drive layer under the chassis for that one feature. This is a Thunder decision, not a Codex one, and it is the only feature where the "library always wins" assumption does not hold.
5. The knee map (row 5) is deliberately dropped in all three, by his rule against stick shaping. Restoring it is his call alone.
6. Library-only capabilities (the last table) are not adopted by default. They are options the pick unlocks, and each one is its own later packet with its own proof, never bundled into the port.

## How the parallel sequences are managed (Thunder's call, Nov 11)

His ruling: during conversion, all three tracks carry the same traits; after the conversion phase ends, each is handled separately. The management spine that makes that true by construction:

- **One shared parity spec:** this document plus the v17 feature list is the single source of truth every track reads. Traits stay identical because they are read from one place, not because three tracks are checked against each other afterward.
- **One branch and one loop per template:** branches `codex/pros-<template>-parity` then `codex/pros-<template>-slew`; loops CX-12 (LemLib), CX-13 (EZ), CX-14 (Okapi) in `OPEN_LOOPS.md`, each with its own named proof. No cross-merging between tracks at any point.
- **One convergence point:** the comparison table at the end, scored on the same criteria for all three, and then his pick. The unpicked branches stay built on disk.
- **After conversion:** each line is managed separately (own branch, own loop, own tune values). The shared spec stops being the authority the day he picks, and the picked line's own docs take over.

## What is still unproven (applies to every row above)

- No library API name in this document is verified against installed headers. Nothing here has compiled. The first build in the cloud environment settles name drift, and the drift fixes stay local to the construction site in each variant.
- Track width is a placeholder (11.5 in, MEASURE ME) in the LemLib and Okapi variants; v17 never recorded it.
- No drive, snap, or heading claim stands in any template until the wheels-up test and the by-hand IMU heading check pass. DRIVE_SIGN is UNVERIFIED on the PROS side in all three.
- Defense return velocity in all three variants is still v17's 60; v18's 40 is one config line in each.
