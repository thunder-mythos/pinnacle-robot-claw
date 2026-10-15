# v12 changes (from v11)

Files: vex_his_v12.py and vex_his_v12.v5python (same project wrapper as v11, new code inside). The IMU is created in code (imu = Inertial(Ports.PORT15)), not in VEXcode's device menu. Don't add it there too.

## What changed
- One CONFIG block at the top ("EDIT THESE"). Every value is tagged [YOU] (you measured/told me), [SPEC] (your motion-profile spec), [MATH] (calculated from other values), [v11] (unchanged), or [GUESS] (not in the spec; a starting value to tune).
- Fixed geometry: WHEEL_DIAMETER 2.75 -> 3.25, DRIVE_GEAR_RATIO now means wheel turns per motor turn = 0.75 (36T motor -> 48T wheel), TRACK_WIDTH 10.0. inches_to_degrees fixed to match.
- IMU on port 15: calibrates at startup, the brain screen shows "IMU calibrating" then "IMU ready". Driver and auton do not move until it's done. If no IMU is found, the screen says "NO IMU on port 15!": heading hold and snaps turn off, and auton turns go back to v11 motor-degree turns.
- New driver pipeline (USE_NEW_DRIVE = True; False = your exact v11 arcade loop):
  1. Deadband + expo on both sticks
  2. Range ceiling with auto-unlock (smoothstep on encoder inches / IMU degrees during a full-stick stroke, falls back with a 0.1 s time constant)
  3. Precision HOLD on R2 (P and k drop, unlock off)
  4. Critically damped shaper per axis with the a_lim(v) envelope, braking cap, and kS
  5. Turn authority |w*| <= a_lat/|v|, plus turn priority (forward speed gives way, the turn never does)
  6. Heading hold on the IMU when the turn stick is centered and you're driving
  All outputs are voltage (spin(..., VOLT)) on a 10 ms loop.
- Fn key = R2 (FN_BUTTON, separate from PRECISION_BUTTON so they can be split later):
  - Fn + Left / Fn + Right = snap 90 left / right. Uses the same quintic IMU turn as auton, works any time in driver, and cancels instantly if a drive stick leaves its deadband. No 180 snap.
  - Fn + Up / Fn + Down = macro_up() / macro_down(). These are stubs that only print their name on the controller screen.
  - Without Fn: Down still toggles rotate like v11. Up/Left/Right do nothing, same as v11.
- R2 spinner binding removed (R1 unchanged). KEEP_R2_SPINNER = True brings it back.
- L1 lift up and L2 lift down are unchanged from v11. A is unbound.
- Auton turns: quintic min-jerk on the IMU with feedforward + PID, error wrapped to +-180. Exit = within tolerance and slow for 5 loops, or timeout. Turns are measured from where auton SHOULD be pointing, so small errors don't pile up.
- Auton drives: S-curve (smoothed trapezoid) on averaged encoders with feedforward + PID + IMU heading hold. Exit = within 0.25 in and slow for 5 loops, or timeout.
- DriveTrain_Forward/Backward/Left/Right keep their signatures (motor degrees) and now call the new code. USE_NEW_AUTON = False puts back v11's spin_for moves.
- Auton numbers rescaled so the robot drives the SAME path as v11. v11's old formula really traveled old x 0.886 (0.75 x 3.25 / 2.75): 22 -> 19.5, 51.3 -> 45.5, 7.3 -> 6.5, 36.7 -> 32.5.
- Turns are now true robot degrees: 230 (old units) -> 180, and Turn_side_inches(1.1) -> Turn_side_robot_degrees(9.7). Conversion: 230 x 3.7 = 851 motor deg. Ideal math with the real wheels says that's 207 deg, but pivots scrub, and your comment calls it "turn around", so 851 motor deg = 180 robot deg. That makes TURN_DEG_PER_ROBOT_DEG = 4.73.
- Simulated auton time: about 13 s (under 15).
- AUTON_TEST setting: "DRIVE24" or "TURN90" makes auton run only that test and print the result on the brain.

## CONFIG values and where they came from
- WHEEL_DIAMETER 3.25, DRIVE_GEAR_RATIO 0.75, TRACK_WIDTH 10.0, MOTOR_FREE_RPM 600, IMU_PORT 15: you
- V_FREE = 600 x 0.75 x pi x 3.25 / 60 = 76.6 in/s; TURN_FREE_DPS = 2 x V_FREE / 10 = 878 deg/s (if no scrub): math
- MU 0.9 (spec 0.8-1.0), KAPPA 0.6 and KAPPA_BRAKE 0.6 (spec 50-70%): spec, middle values
- A_TRACTION = 0.6 x 0.9 x g = 208 in/s^2: math
- A_MOTOR ~392 in/s^2: math from blue stall torque, gearing, and wheel radius. Uses ROBOT_WEIGHT_LB 15 = GUESS, weigh it.
- A_BRAKE = min(kappa_b x mu x g, g x d/h): spec formula. CG_TIP_RATIO (d/h) 1.0 = GUESS, measure it.
- A_LAT = same traction budget (208 in/s^2): GUESS (the spec has the formula but no number)
- KV = 12/V_FREE, KA = 12/A_MOTOR: math (replace with characterization runs)
- KS 0.5 V, KS_RAMP_IN_S 1.0, TURN_FF_SCALE 1.0: GUESS
- Deadbands .06/.08, expo .55/.75 (precision .35/.40), L0 .65/.40, unlock 18 in / 25 deg, stroke .85/.60, fall-back 0.1 s, precision P .30/.25: spec
- DRIVER_DRIVE_MAX = V_FREE, DRIVER_TURN_MAX = TURN_FREE_DPS: math
- WN_UP 17.5 (spec 15-20), WN_DOWN = 1.75 x WN_UP (spec 1.5-2x): spec, middle values
- HEADING_HOLD on (spec). HEADING_HOLD_KP 4.0, MAX 60 deg/s, CAPTURE 10 deg/s, MIN_SPEED 2 in/s: GUESS
- SNAP_DEG 90: you. SNAP_MAX_DPS 350: GUESS. SNAP_MAX_ACCEL_DPS2 ~2390: math (traction)
- AUTON_DRIVE_SPEED 25: v11. AUTON_V_MAX = 25% of V_FREE = 19.1 in/s (same top speed as v11; the spec allows up to 85-90%)
- AUTON_ACCEL = A_TRACTION: spec. AUTON_JERK_TIME 0.10 s: GUESS
- DRIVE_KP 0.8, DRIVE_KD 0.05, DRIVE_HEADING_KP 0.15, DRIVE_HEADING_MAX_V 3: GUESS. DRIVE_TOL_IN 0.25: spec
- AUTON_TURN_MAX_DPS 350: GUESS. Picked to keep the turn-around about as quick as v11, since a quintic's peak is 1.875x its average. AUTON_TURN_ACCEL_DPS2 ~2390: math
- TURN_KP 0.25, TURN_KI 0, TURN_KD 0.02, TURN_SETTLE_DPS 5, SETTLE_LOOPS 5, SETTLE_MARGIN_SEC 0.5: GUESS. TURN_TOL_DEG 1.0: spec (0.5-1)
- TURN_DEG_PER_ROBOT_DEG 4.73 = 851/180: math (see above)
- LIFT_DEG_PER_INCH 50 (still unmeasured), LIFT_MAX 900, LIFT_DOWN_SPEED 50, DRIVER_DRIVE/TURN_SPEED .6/.5, AUTON_PAUSE_MS 800, CLAW_CLOSED_OUTPUT False, timeouts 3 s / 2 s: v11
- LOOP_MS 10: spec

## Test these first, in order
1. IMU calibration: power on with the robot still. The brain should show "IMU calibrating", then "IMU ready" after ~2 s. "NO IMU on port 15!" means check the cable.
2. Drive 24 in: set AUTON_TEST = "DRIVE24" and run auton. Tape-measure the move. The brain shows encoder inches and heading drift. If the tape disagrees with 24, the gear ratio or wheel number is off: scale DRIVE_GEAR_RATIO by tape/24.
3. Snap 90: in driver, hold R2 and tap Right. It should turn 90 smoothly and stop dead. Also try AUTON_TEST = "TURN90". If it lags or stops short, raise TURN_FF_SCALE (scrub) or TURN_KP. If it overshoots, raise TURN_KD.
Then: find KS (raise volts until the robot just creeps), drive normally to feel unlock/precision/heading hold, and set AUTON_TEST back to "NONE" for matches.
