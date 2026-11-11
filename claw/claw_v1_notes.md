# claw_v1 notes (fresh series)

Rebuilt from v20's numbers and architecture on Oct 16, 2026. Same constants, same behavior, same bug fixes. Dropped: the v11 fallback code paths, the dead R2 spinner callbacks, the MaxSpeed leftover, the unused pause constant, and every comment. The code file has zero comment lines.

## Macros

Three slots on Fn+X, Fn+Y, Fn+A (direct press does nothing except Y, which toggles tilt). Step lists MACRO_X_STEPS, MACRO_Y_STEPS, MACRO_A_STEPS are all empty. Sticks are dead during a macro. The only kill is a fresh press of R2 (the Fn button) after release. Fn plus arrow while a macro runs does nothing. MACRO_CANCEL_STICK is gone.

## Versions

- v1: first fresh rebuild. Parked on Drive.
- v2 (Oct 16 evening): merged Thunder's `claw_v1-thunder.v5python` micro-edits (his "SELF-TUNED" constants header, his `if True: # MACHINERY` pack label, constants in their own collapsible block) with Corvin's block moves (bindings/auton primitives/driver loop/tests packed, Fn+X/Y/A macros) on top. VERSION = 2. Pushed as new files, v1 left parked.

## File layout (Oct 16 evening, Thunder's order)

Section headers are labeled comments. Everything he never touches sits in one `if True:` block he can collapse.

1. DEVICES
2. CONSTANTS YOU TUNE (sub-headers per group)
3. MACHINERY, inside `if True:`, never touch (also holds driver_loop and run_auton_test per his re-pack order)
4. AUTON - YOUR RUNS (run_autonomous first, then primitives)
5. MACROS - YOUR STEPS GO HERE
6. BUTTON BINDINGS
7. WHEN STARTED

## Files

- `claw_v1.py`: the program. Zero comment lines. Console clear `print("\033[2J")` appears exactly once (line 25).
- `claw_v1.v5python`: built Oct 16 from v20's wrapper. One line of JSON, same key order. Region copied from v20 byte for byte except the PneumaticRotate spelling fix. robotConfig unchanged at 15 entries, no IMU. Body is the .py after the console clear. Validated: JSON parses, textContent parses as Python, no device redefinitions in the body.
- Tab owns the .v5python lane; the spelling fix was Thunder-confirmed Oct 16.

## Tags

- **YOU** = Thunder measured it or chose it
- **SPEC** = his motion-profile spec, starting value
- **GUESS** = placeholder, needs his solid answer
- **MATH(inputs)** = computed; inputs listed so a bad input can't hide

## Constants

### Master

| Constant | Value | Tag |
|---|---|---|
| AUTON_TEST | "NONE" | YOU |

### Drive heading (inertia PID)

| Constant | Value | Tag |
|---|---|---|
| DRIVE_HEADING_KP | 0.15 | GUESS |
| DRIVE_HEADING_MAX_V | 3.0 | GUESS |
| DRIVE_DISTANCE_SCALE | 1.116 | YOU |

The encoder drive PID is dropped from the design. Its constants (DRIVE_KP, DRIVE_KD, DRIVE_TOL_IN, DRIVE_SETTLE_SPEED) and the flag are gone from the code.

### Turn PID

| Constant | Value | Tag |
|---|---|---|
| TURN_KP | 0.25 | GUESS |
| TURN_KI | 0.0 | GUESS, off |
| TURN_KD | 0.02 | YOU |
| TURN_TOL_DEG | 1.0 | SPEC |
| TURN_SETTLE_DPS | 5.0 | GUESS |

### Settle

| Constant | Value | Tag |
|---|---|---|
| SETTLE_LOOPS | 5 | GUESS |
| SETTLE_MARGIN_SEC | 0.5 | GUESS |

### Buttons

| Constant | Value | Tag |
|---|---|---|
| PRECISION_BUTTON | "R2" | YOU |
| FN_BUTTON | "R2" | YOU |
| FN_SNAP_LEFT | "Left" | YOU |
| FN_SNAP_RIGHT | "Right" | YOU |
| FN_MACRO_UP | "Up" | YOU |
| FN_MACRO_DOWN | "Down" | YOU |
| AUTON_SIDE | "RIGHT" | YOU |

### Geometry

| Constant | Value | Tag |
|---|---|---|
| WHEEL_DIAMETER | 3.25 in | YOU, tape unverified |
| DRIVE_GEAR_RATIO | 0.75 | YOU, tooth count unverified |
| TRACK_WIDTH | 10.0 in | YOU |
| MOTOR_FREE_RPM | 600 | YOU, blue confirmed |
| ROBOT_WEIGHT_LB | 15.0 | GUESS, never weighed |
| CG_TIP_RATIO | 1.0 | GUESS, never measured |

### Derived

| Constant | Value | Tag |
|---|---|---|
| V_FREE | 76.58 in/s | MATH(YOU, YOU, YOU) |
| TURN_FREE_DPS | 877.6 deg/s | MATH(MATH, YOU) |
| MU | 0.9 | SPEC |
| KAPPA | 0.6 | SPEC |
| KAPPA_BRAKE | 0.6 | SPEC |
| A_MOTOR | 392.5 in/s^2 | MATH(YOU, YOU, YOU, GUESS) |
| A_TRACTION | 208.5 in/s^2 | MATH(SPEC, SPEC) |
| A_BRAKE | 208.5 in/s^2 | MATH(SPEC, SPEC, GUESS) |
| DRIVER_BRAKE_SCALE | 0.7 | YOU |
| A_LAT | 208.5 in/s^2 | MATH(SPEC, SPEC) |
| KV | 0.1567 V per in/s | MATH(MATH) |
| KA | 0.0306 V per in/s^2 | MATH(MATH incl GUESS) |
| KS | 0.5 V | GUESS |
| KS_RAMP_IN_S | 1.0 s | GUESS |
| TURN_FF_SCALE | 1.0 | GUESS |

### Driver

| Constant | Value | Tag |
|---|---|---|
| DRIVE_DEADBAND | 0.06 | SPEC |
| TURN_DEADBAND | 0.08 | SPEC |
| DRIVE_EXPO | 0.55 | SPEC |
| TURN_EXPO | 0.75 | SPEC |
| DRIVE_EXPO_PRECISION | 0.35 | SPEC |
| TURN_EXPO_PRECISION | 0.40 | SPEC |
| DRIVE_L0 | 0.65 | SPEC |
| TURN_L0 | 0.55 | YOU |
| DRIVE_UNLOCK_IN | 18.0 in | SPEC |
| TURN_UNLOCK_DEG | 25.0 deg | SPEC |
| STROKE_START | 0.85 | SPEC |
| STROKE_END | 0.60 | SPEC |
| UNLOCK_FALL_TAU | 0.10 s | SPEC |
| DRIVE_PRECISION | 0.30 | SPEC |
| TURN_PRECISION | 0.35 | YOU |
| WN_UP | 17.5 rad/s | SPEC |
| WN_DOWN | 30.6 rad/s | MATH(SPEC) |
| HEADING_HOLD | True | SPEC |
| HEADING_HOLD_KP | 4.0 | GUESS |
| HEADING_HOLD_MAX_DPS | 60.0 | GUESS |
| HEADING_CAPTURE_DPS | 10.0 | GUESS |
| HEADING_HOLD_MIN_SPEED | 2.0 in/s | GUESS |

### Snaps

| Constant | Value | Tag |
|---|---|---|
| SNAP_DEG | 90 | YOU |
| SNAP_MAX_DPS | 350.0 | YOU |
| SNAP_ACCEL_SCALE | 1.0 | YOU |
| TURN_TRACTION_ACCEL_DPS2 | 2389 deg/s^2 | MATH(MATH, YOU) |
| SNAP_MAX_ACCEL_DPS2 | 2389 deg/s^2 | MATH(MATH, YOU) |

### Auton

| Constant | Value | Tag |
|---|---|---|
| AUTON_DRIVE_SPEED | 25 % | YOU |
| AUTON_V_MAX | 19.14 in/s | MATH(YOU, MATH) |
| AUTON_ACCEL | 208.5 in/s^2 | SPEC |
| AUTON_JERK_TIME | 0.10 s | GUESS |
| AUTON_TURN_MAX_DPS | 350.0 | GUESS |
| AUTON_TURN_ACCEL_DPS2 | 2389 deg/s^2 | MATH(MATH) |

### Lift

| Constant | Value | Tag |
|---|---|---|
| LIFT_DEG_PER_INCH | 64 | YOU, measured once |
| LIFT_MAX_DEGREES | 900 | YOU |
| LIFT_DOWN_SPEED | 50 % | YOU |
| LIFT_DRIVER_SPEED | 50 % | YOU |
| LIFT_BRAKE_SCALE | 0.7 | YOU |
| LIFT_RAMP_SEC | 0.2 s | GUESS |
| TIP_GUARD_LIFT_DEG | 425 | YOU |
| TIP_GUARD_DRIVE_SCALE | 0.50 | YOU |
| TIP_GUARD_RELEASE_DEG | 400 | GUESS |

### Misc

| Constant | Value | Tag |
|---|---|---|
| CLAW_CLOSED_OUTPUT | False | YOU |
| LIFT_MOVE_TIMEOUT_SEC | 2 s | YOU |
| LOOP_MS | 10 ms | SPEC |

### Downstream warnings

- KA carries the unweighed 15 lb
- A_BRAKE carries the unmeasured tip ratio 1.0
- DRIVE_DISTANCE_SCALE now only scales the test telemetry readouts

## What the code does, plain words

Driver: sticks go through deadband, expo curve, a ceiling that unlocks to full power on sustained pushes, and a shaper that smooths starts and stops. R2 held drops to precision mode and doubles as the Fn key. Fn plus arrows snaps 90 degrees or runs macros. Heading hold keeps the robot straight when driving with the turn stick centered.

Auton: drives follow an S-curve speed plan with feedforward volts plus IMU heading correction. The encoder drive PID is dropped, so drives end when the plan ends. Turns follow a quintic plan on the IMU with PD correction. The sequence is literal numbers with settle waits: claw close, wait 0.8 s, lift up 6.5, forward 38, wait 0.8 s, turn 9.7 right, wait 0.8 s, forward 45.5, lift down 8, wait 0.8 s, claw open, wait 0.5 s, back 6.5, turn 180, forward 32.5.

Macros: Fn+Up and Fn+Down run step lists. Both are empty. Steps can be drive, turn, lift_up, lift_down, claw, wait. Any stick past 20 percent or Fn plus the same arrow cancels.

Tests: set AUTON_TEST to DRIVE24, TURN90, or TUNE. TUNE runs drive 24, turn 90, turn -90, drive -24 and prints errors. Tape-measure everything, the screen numbers come from encoders.

## What was dropped from v20 and why

v11 fallback loops (USE_NEW_DRIVE/USE_NEW_AUTON False paths, legacy motor-degree turns): Thunder rejected the rollback, keeping them was dead weight.
KEEP_R2_SPINNER callbacks: never registered, dead code.
MaxSpeed global: v4 leftover, nothing reads it.
AUTON_PAUSE_MS: unused, the routine uses literal waits.
TURN_DEG_PER_ROBOT_DEG: only the legacy turns used it.
inches_to_degrees / motor_deg_to_inches round trip: the scale canceled itself out, so auton_drive takes inches directly now.
PueumaticRotate typo: fixed to PneumaticRotate.

## Bug fixes carried over

Mirrored steering, lift hard limits at 0 and 900, claw first-press fires, IMU missing falls back cleanly with a screen warning, macros cancel cleanly, lift holds position on stop, auton ends with drive on coast for driver control.

## The one exception to zero comments

The .v5python wrapper keeps VEXcode's own generated header block untouched. That block is machine boilerplate and altering it risks the corrupt-file rejection seen on v13/v14. Everything Corvin and Tab wrote has no comments.

## Tuning guidance

Do not touch gains until the robot is mechanically tight and the IMU mount is rigid. Then: one taped drive, one taped turn, scale the typed numbers. Gains are not the problem until repeatability is proven.
