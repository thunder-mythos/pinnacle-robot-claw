# pinnacle-robot-claw

VEX V5 robot code for RECF Achieve (Pinnacle). VEXcode Python, single file: `src/main.py` (V5 Python can't run multi-file projects).

## Setup (VS Code)
1. Install the **VEX Robotics** extension (VEXRobotics.vexcode).
2. Clone this repo and open the folder.
3. Let the extension set up the project. VEX icon > Import Project works with a `.v5python` file. Or create a V5 Python project and put this `src/main.py` in it. Commit `.vscode/vex_project_settings.json` and `extensions.json`. Don't commit `settings.json`, which is machine-specific and already gitignored.
4. Plug in the brain over USB and click Download.

Note: the extension cuts project names over 13 characters short, so set the project name to something short, like `pinnacle-v5`.

## Ports
| Device | Port |
|---|---|
| Drive left L1/L2/L3 (reversed) | 8 / 9 / 10 |
| Drive right R1/R2/R3 | 1 / 2 / 3 |
| Lift LiftL1 / LiftL2 | 6 / 7 |
| Lift LiftR1 / LiftR2 (reversed) | 5 / 4 |
| Rear spinner | 21 |
| Inertial sensor | 15 (created in code, not in the device menu) |
| 3-wire: claw / tilt / rotate | G / F / H |

Drive: 6 blue 600 rpm motors, 36T motor to 48T wheel (0.75), 3.25" wheels, 10" track width.

## Buttons (driver)
| Button | Action |
|---|---|
| L1 / L2 | Lift up / down |
| R1 | Rear spinner |
| R2 (hold) | Precision mode, and the Fn key |
| R2 + Left / Right | Snap turn 90 degrees |
| R2 + Up / Down | Macro slots (empty for now) |
| B | Claw toggle |
| Y | Tilt toggle |
| Down | Rotate toggle |
| X | Lift coast for 1 s, then hold (reset) |

## First tests
1. Power on and wait for "IMU ready" on the brain.
2. Set `AUTON_TEST = "DRIVE24"`, run auton, and check it with a tape measure.
3. Hold R2 and tap Right to check the snap turn.
4. Log the results in `docs/tuning_log.md`.

Fallbacks: `USE_NEW_DRIVE = False` / `USE_NEW_AUTON = False` restore v11 behavior.

## Git habits
- Commit before each tuning session.
- Tag what runs at each event: `git tag comp-YYYY-MM-DD`.
