# v14 changes

Format-only reformat of v13 into the VS Code V5 project template. **No behavior changes**: no gains, constants, logic, button bindings, timing or order of execution changed.

## What moved / was renamed
- Added the VS Code template header block on top (Module main.py, Author viraa, Created 10/15/2026, 10:06:25 PM, Description).
- `# Library imports` above `from vex import *` (plus `import urandom`, `import math`, which v13 already used).
- `brain=Brain()` -> `brain = Brain()` (spacing only), robot config right after it, all config lines unchanged.
- Removed the `#region VEXcode Generated Robot Configuration` / `#endregion` marker comments.
- Renamed `vexcode_auton_function` -> `autonomous` and `vexcode_driver_function` -> `user_control`.
- Renamed the competition variable `competition` -> `comp` (used inside those two functions to check auton/driver state): `comp = Competition(user_control, autonomous)` under `# create competition instance`.
- Added `# actions to do when the program starts` above the event handler registrations, `wait(15, MSEC)` and `when_started1()`. Same order as v13.

## Kept in v13 order on purpose
- The startup lines that were inside the old VEXcode config block (`wait(30, MSEC)`, random seed, `wait(200, MSEC)`, console clear) stay right after the robot config, where they ran in v13. Moving them to the bottom would change the startup timing.
- `autonomous()` / `user_control()` stay near the bottom, right before `comp = Competition(...)`, so everything they start (`onauton_autonomous_0`, `ondriver_drivercontrol_0`) is defined first, exactly like v13.
- The template's trailing `brain.screen.clear_screen()` was NOT added, because v13 never cleared the screen there and that would be a behavior change.

## Verification
- `py_compile` / `ast.parse`: OK.
- Whole-file AST check: v13 with the three renames applied (`vexcode_auton_function`, `vexcode_driver_function`, `competition`) produces an AST identical to v14 (257 top-level statements, same order).
- All 87 other functions/classes: identical AST, unchanged.
- All 145 module-level assignments: identical source, except `competition` -> `comp`.
- Every v13 comment is still there, except the two region markers and `# register the competition functions` (now `# create competition instance (registers the competition functions)`).
