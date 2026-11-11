# CONTEXT.md: Standing Context for the Robotics Code Work Lane

Read after AGENTS.md. This is where things stand, what the team is trying to do, what research is live, and who does what by role. Dated facts are as of Nov 11, 2026; when a fact here and the registry disagree, check `OPEN_LOOPS.md`, and when this file and a packet disagree, the packet wins for that task and the disagreement gets flagged.

## Where we currently stand

**The code.** The robot program is the claw series, VEXcode Python. claw_v17 is the current delivered version (delivered to Thunder and to Drive as new versioned files). claw_v18 exists locally only: exactly one line different from v17 (DEFENSE_RETURN_VEL 60.0 to 40.0, Thunder's ordered value), awaiting his push-or-kill. Version discipline: every change is a new versioned file pair (.py plus .v5python); named versions are never overwritten.

**What v17 does.** Four-motor drive (blue 6:1) and four-motor lift (green 18:1). Drive modes flipped at Thunder's order: regular mode is the slow mode starting at 30 percent, Function (held, R2) is the fast mode starting at 70 percent, and turn is 60 percent of the active mode's drive value (18 regular, 42 Function). The Up/Down adjustment is separate per mode (plain arrows for regular, Fn plus arrows for Function), steps of 10, persists through a match, resets on restart. The claw closes first thing at startup, before motor setup and before IMU calibration, and the auton does only three things: close the claw, wait half a second, raise the lift one inch. Full device map: drive L1 Port 10, L2 Port 9, R1 Port 1 reversed, R2 Port 2 reversed; lift LiftL1 Port 7, LiftL2 Port 6, LiftR1 Port 4 reversed, LiftR2 Port 5 reversed; IMU Port 15; claw pneumatic on three-wire port A; RearSpinner Port 21 kept in code, its hardware is removed.

**The open sensor problem.** Snap turns spun multiple revolutions on hardware under both turn signs. The standing read is that the IMU heading value may not be changing at all while the robot rotates. Two physical tests gate everything in that area and neither has been reported done: rotating the bot by hand and watching the heading value move, and a wheels-up test confirming forward is forward. Until they pass, drive direction, snap turns, and heading hold are unproven, in this stack and any other.

**The Codex route.** Thunder confirmed Cloud plus CLI dispatch on Nov 10, 2026: Corvin dispatches cloud tasks from the VM's Codex CLI once it is signed in by device auth, Thunder watches and steers in his ChatGPT desktop app, and GitHub (thunder-mythos/pinnacle-robot-claw) is the home for the claw series. The sequence from here: VM sign-in first, then commit the claw series into the repo, then Thunder publishes the cloud environment, then the pilot (FLM-V2-PILOT-001, the v18 reproduction, re-aimed to a commit-based proof) fires. Setup is done to the login wall; sign-in has not happened.

**PROS.** The switch is undecided. Thunder's word: the code is likely heading toward PROS and more comes from him later. Preparation exists (plain scaffold mirroring v17, three template variants, a transition protocol) so the call, if it comes, is execution rather than research. The Python claw series remains the competition code until he says otherwise.

**The season clock.** The team's path runs through the JROTC National Championship in Reno, NV (Mar 6 to 7, 2027), qualifying toward RECF Worlds in St. Louis (Apr 27 to May 6, 2027). Code decisions are made against that clock: nothing unproven rides to Reno.

## The team's code goals

- **Reliability before features.** The same code must behave the same way every match. No untested value rides on the robot, and a version is never called validated from a desk check.
- **Driver feel as a designed thing.** Two drive modes (precise regular, fast Function) with separate on-the-fly adjustment, per-motor control so drift is corrected per motor, and torque always at full with speed doing the work.
- **A simple, safe auton that grows only on proof.** Today it closes the claw and raises the lift a small amount. It earns more steps by working, not by planning.
- **Close the movement-quality gap without betting the season.** The smooth, planted movement of the PROS teams is the target quality bar; the plan is to take the pieces in ranked order (slew limiting first), in whichever stack Thunder calls, and never let a framework switch eat the season.
- **Serve the judged story.** The custom 3D printed claw is the team's Innovate centerpiece, and the code supports it directly (the claw is set closed from the first instant of startup). Code decisions stay legible, because the engineering notebook tells this story to judges.

## Research on top (what shapes how tasks get executed)

- **PROS movement research (Nov 7, 2026; full text in `pros-movement-research.md`).** PROS itself is not the smoothness: core PROS ships no chassis PID, slew limiter, odometry, or stick curve. The glide is built on top by libraries and hardware, ranked: (1) slew rate limiting, (2) tuned PID on distance and heading together with settle-band exits, (3) motion chaining and pure pursuit in auton, (4) exponential stick curves plus active braking in driver control, (5) hardware (omni rollers, bearings, low centered weight), (6) the V5 motor's own internal PID that every bot gets. Some of it is replicable in the current Python stack (a true slew limiter, stick curves, a 10 ms loop, light active brake); odometry, pose moves, and path following effectively require PROS with a library plus tracking wheels and days of tuning. The report's bluntest point stands above all of it: fixing the IMU outranks every movement upgrade, because a frozen heading breaks the advanced stacks the same way it breaks the simple ones.
- **FLM-V2 scoping (Nov 9, 2026).** Codex fits this lane only as a candidate-producing worker: patch drafting, wrapper generation, validation runs, read-only audits. It never chooses values, pushes, delivers, or makes hardware claims. Every harness rule in AGENTS.md descends from that finding.

## The team, by silhouette

No names here by design; roles are what the work needs.

- **The Programmer.** Owns the code end to end: every constant, every version, every gate. Works in short directives and expects finished, verified work back, not options essays. Translates everyone else's input (a wiring change, a feel report, a tournament deadline) into code decisions, and owns the values personally: a number he has not approved does not ship.
- **The Driver.** Drives the robot in matches. Reports behavior in plain feel language (floaty, coasts too long, spins past the mark), and those reports are ground truth for tuning: the programmer's job is to translate feel into constants, never to argue the feel away. What the driver asks for mid-season is what the mode and adjustment design exists to serve.
- **The CAD and Build hand.** Owns the mechanical side: the 3D printed claw's design trail, the physical build, and the wiring. Wiring truth flows from this role: when a motor moves ports or a device comes off the bot, that fact reaches the programmer before code assumes it, because the code's device map is only ever as true as the last wiring report.
- **The Notebook Keeper.** Owns the engineering notebook, the judged record: design decisions, tests, and results written as they happen, in the team's own words. Code work feeds it (version changes, test outcomes, design reasoning), and it is why changes stay legible and dated.
- **The Coach.** Owns tournament logistics and announcements: registrations, schedules, league and championship decisions. Code deadlines bend around the tournament calendar this role publishes.

How they work together: build changes wiring, wiring reaches the programmer, the programmer ships a version, the driver runs it and reports feel, the programmer tunes from the report, and the notebook records the whole loop. Codex sits outside that loop as execution help for the programmer's lane only; it does not replace any role in it.

## Known unknowns (never assume past these)

- Whether the IMU heading value changes when the robot rotates (by-hand check, not done).
- Whether forward command is forward on the current wiring (wheels-up test, not done; the drive sign in code is UNTESTED).
- Every defense-mode value, the one-inch auton lift raise, and the per-mode drive values are UNTESTED on hardware until Thunder reports runs.
- Where a real PROS compile will live when the switch is called (this VM has no PROS toolchain or ARM cross-compiler; the cloud environment question is open with it).
- Whether v18 gets pushed or killed, and whether PROS gets called at all. Both are Thunder's, and silence on either means not yet.
