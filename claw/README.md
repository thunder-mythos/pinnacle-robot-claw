# Claw Series (VEXcode Python)

The robot program for team Achieve_65714X "Screamin' Eagles", RECF Achieve, game Pinnacle. Every version is a pair: `claw_vN.py` (the program) and `claw_vN.v5python` (the VEXcode project wrapper built from it by a fixed recipe). A .py and its .v5python are one deliverable; never ship one without the other.

- **Current delivered version: v17.** Drive modes flipped at Thunder's order: regular is the slow mode starting at 30%, Function (R2 held) is the fast mode starting at 70%, turn is 60% of the active mode's drive value, per-mode Up/Down adjustment in steps of 10. The claw closes first at startup; auton closes the claw, waits 500 ms, raises the lift 1 inch.
- **v18 exists locally in this import, one line different** (DEFENSE_RETURN_VEL 60.0 to 40.0), awaiting Thunder's push-or-kill. It is not the delivered version.
- **Version rule:** every change is a new versioned file pair. Named versions are never overwritten, and history is never rewritten.
- **Device map:** drive L1 Port 10, L2 Port 9, R1 Port 1 reversed, R2 Port 2 reversed (blue 6:1); lift LiftL1 Port 7, LiftL2 Port 6, LiftR1 Port 4 reversed, LiftR2 Port 5 reversed (green 18:1); IMU Port 15; claw pneumatic on three-wire port A; RearSpinner Port 21 kept in code, hardware removed.
- **Guardrails:** per-motor factors are scales, not caps; drive torque stays 100, slowing by speed only; every new tune variable is labeled UNTESTED or MATH-VERIFIED; no claim about drive direction, snap turns, or heading hold until the by-hand IMU heading check and the wheels-up test pass. The full harness lives in `codex/` in this repo (start at `AGENTS.md` in the repo root).
- The older program line (v16 to v20, `src/main.py`) is untouched by this import and stays on main as history.
