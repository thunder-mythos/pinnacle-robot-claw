# v13 changes (from v12)

Approved by Viraaj on the phone, Oct 15 2026. Single file: src/main.py. Checked only for Python syntax and undefined names. **Not tested on the robot yet.** Practice on Fri Oct 16 is the first real test.

## Values (old -> new)
| Setting | v12 | v13 | Why |
|---|---|---|---|
| TURN_L0 | 0.40 | 0.55 | Turning was too slow (moderate bump, in proportion with precision) |
| TURN_PRECISION | 0.25 | 0.35 | Fn/precision turning didn't move the robot. Max went from 10% to 19% |
| LIFT_DEG_PER_INCH | 50 | 64 | Measured 320 deg / 5 in. Re-measure at low lift speed |
| DRIVE_DISTANCE_SCALE | (none) | 1.116 | DRIVE24 test went 21.5 in for 24 commanded |
| TURN_KD | 0.02 | 0.03 | Damp the end of turns |
| SNAP_MAX_DPS | 350 | 250 | Smoother snaps |
| SNAP_MAX_ACCEL_DPS2 | ~2390 | ~1430 (x0.6, SNAP_ACCEL_SCALE) | Smoother snaps. Auton turns keep the full ~2390 (new name TURN_TRACTION_ACCEL_DPS2) |
| TIP_GUARD_LIFT_DEG | (none) | 425 | Tip guard on above this lift angle |
| TIP_GUARD_DRIVE_SCALE | (none) | 0.50 | Drive at 50% of normal while the guard is on. Turning is not capped |
| TIP_GUARD_RELEASE_DEG | (none) | 400 [GUESS] | Guard turns off below this, so it doesn't flicker at 425 |
| LIFT_DRIVER_SPEED | 50 (hard-coded) | 50 | Same speed, now a named setting |
| LIFT_RAMP_SEC | (none) | 0.2 [GUESS] | L1/L2 ramp up/down time |
| MACRO_CANCEL_STICK | (none) | 0.20 [GUESS] | A stick past 20% cancels a running macro |

## What changed in the code
- **TUNING block** at the top of the CONFIG section: every PID knob is in one place, with a note on what raising it does. DRIVE_KP, DRIVE_KD, DRIVE_HEADING_KP, DRIVE_HEADING_MAX_V, DRIVE_TOL_IN, DRIVE_SETTLE_SPEED, TURN_KP, TURN_KI, TURN_KD, TURN_TOL_DEG, TURN_SETTLE_DPS, SETTLE_LOOPS, SETTLE_MARGIN_SEC and DRIVE_DISTANCE_SCALE moved there. Only TURN_KD changed value. The PID code itself (auton_drive, auton_turn / QuinticTurn) was not rewritten.
- **AUTON_TEST = "TUNE"**: the robot drives 24 in, turns 90, turns -90, then drives -24, about 5 s total. After each step it shows the distance error (e, inches, + = stopped short) and the heading error (h, degrees) on the brain screen, the controller and the console.
- **Drive distance scale**: inches_to_degrees multiplies by DRIVE_DISTANCE_SCALE. motor_deg_to_inches and drive_speed_in_s divide by it. The two conversions are exact inverses, so the scale is applied once. Set it to 1.0 to turn it off.
- **Tip guard**: tip_guard_drive_scale() reads LiftL1. Both driver loops (v12 pipeline and the v11 fallback) multiply only the forward/back part by it. In the v12 pipeline, the shaper brings the speed down smoothly, with no sudden brake.
- **Lift ramp**: L1/L2 now ramp 0 -> 50% over 0.2 s. On release they ramp 50% -> 0, then stop on HOLD. The 0 and 900 limits still stop the lift right away.
- **Macro framework**: run_macro(name, arrow, steps) with the steps "drive", "turn", "lift_up", "lift_down", "claw" and "wait". It uses auton_drive, auton_turn, Lift_Up_inches/Lift_Down_inches and claw_set. Turns are measured from where the robot points when the macro starts. To cancel: push any stick past 20%, or press Fn + the same arrow again. Everything stops (drive brakes, lift holds). While a macro runs, the driver loop doesn't touch the drive. MACRO_UP_STEPS and MACRO_DOWN_STEPS are EMPTY: the controller shows "macro_up: empty". There's a commented example.
- lift_Up_degrees / lift_Down_degrees / Lift_Up_inches / Lift_Down_inches take an optional wait_done (default True, same as before). Macros pass False so a lift move can be cancelled.
- auton_drive / auton_turn loops break early only if a running macro is cancelled. In auton this is always False.

## Watch out for
- **Auton path gets longer.** The auton distances (19.5, 45.5, 6.5, 32.5) were set to match v11's motor degrees. With the 1.116 scale, every drive is now ~11.6% longer in real life than in v12. Run the auton once and check it.
- Driver auto-unlock (DRIVE_UNLOCK_IN 18 in) is now measured in real inches, so it unlocks ~10% later. Small change.
- The feedforward KV still uses the ideal wheel math. If drives lag their plan (the TUNE test shows them stopping short before the PID catches up), raise KS/KV a little or let DRIVE_KP do it.
- The tip guard and lift limits use LiftL1's encoder, which reads 0 wherever the lift was at power-on (auton also zeros it). Power on with the lift at the bottom.
- Macros with no IMU fall back to v11 motor-degree turns, and those can't be cancelled partway through a turn.
