# HARNESS.md: Folder Structure and File Info

The map of this lane. Every file Codex may meet, what it holds, and how it connects to the rest. If a file is not described here, treat it as unknown and ask through your report rather than assuming.

## The tree

```text
~/workspace/robotics-fresh/
  claw_v1.py ... claw_v18.py            versioned robot code, Python (VEXcode)
  claw_v1.v5python ... claw_v18.v5python  the wrapper paired with each .py
  claw_v1_notes.md                      historical notes from the first rebuild
  pros-movement-research.md             the PROS movement research report
  pros-transition-protocol.md           how the PROS switch runs, if called
  pros-scaffold/                        plain PROS (C++) scaffold, mirrors v17
  pros-templates/                       PROS template variants (candidate bases)
    ez-template/  lemlib/
  codex/                                the Codex harness (this folder)
  build/                                scratch and reference material, not source

~/workspace/robotics-fresh/codex/
  AGENTS.md                             standing instruction, read first
  CONTEXT.md                            where things stand, goals, people, unknowns
  HARNESS.md                            this file
  OPEN_LOOPS.md                         this lane's registry of open work
  README.md                             setup state and the packet format
  packets/                              task packets, the only task source
  runs/<packet-id>/                     one envelope per run
    input/  work/  output/  report/
```

On the cloud route, the claw series lives in the GitHub repo (thunder-mythos/pinnacle-robot-claw) and this harness ships with it: AGENTS.md at the claw folder root, the rest alongside. The local tree above stays the working mirror.

## The claw series (the code itself)

- **claw_vN.py** is one full version of the robot program in VEXcode Python. Versions are never edited after delivery; a change means a new version file. The series runs v1 (Oct 16, 2026 clean rebuild) through v18.
- **claw_vN.v5python** is the VEXcode project wrapper paired with the same-numbered .py. It is generated from the .py by a fixed recipe (one-line JSON; textContent is the device region block, two newlines, then the .py body after the console-clear line; the IMU is defined in the body, never in robotConfig). A .py and its .v5python are one deliverable: never ship one without the other, never let them drift.
- **Current state:** v17 is the delivered version (chat plus Drive). v18 exists locally only, one line different (DEFENSE_RETURN_VEL 40.0), awaiting Thunder's push-or-kill. Details and the full device map are in `CONTEXT.md`.
- **claw_v1_notes.md** is history from the first rebuild, kept for provenance. It contains values from before the no-guesses rule; never source a value from it.

## The PROS side (preparation, not adopted)

- **pros-scaffold/** is a plain PROS C++ project that mirrors claw_v17 feature by feature (kernel 4.2.0; src: main, robot_config, drive, driver, mechanisms, auton; include: config.hpp, robot.hpp, main.h). It exists so a PROS switch, if Thunder calls it, starts from a port instead of a blank page. It has never been compiled against a real PROS kernel on this machine and has never run on a brain.
- **pros-templates/** holds two public template projects (ez-template, lemlib), each a full PROS project tree. They are candidate bases for the movement layer, to be built as separate branches and compared if the switch is called. None is adopted; none outranks the plain scaffold until Thunder picks. (OkapiLib was a third candidate, dropped Nov 11, 2026.)
- **pros-transition-protocol.md** is the adoption plan: step order, the validation standard per step, and where Thunder's gates sit. It executes only on his call.
- **pros-movement-research.md** is the evidence base for the movement work: why PROS bots look smooth (library slew limiting first, then PID with settle exits, then chaining and stick curves, then hardware), what is replicable in the current Python stack, and what genuinely needs PROS. Read it before any movement-related packet.

## The harness folder (codex/)

- **AGENTS.md** is the standing instruction: roles, the First and Last Mile concept, the work ethic, the startup ritual, stop conditions, guardrails. It is the first file read in every session.
- **CONTEXT.md** is the standing context: where the work currently stands, the team's code goals, the research on top, the team by role silhouette, and the known unknowns. It changes as facts change; when it and a packet disagree, the packet wins for that task and the disagreement gets flagged in the report.
- **PROCEDURE.md** is the run procedure: the nine steps every Codex run follows, and the run log rules (hierarchical markdown, frontmatter, append-only).
- **OPEN_LOOPS.md** is this lane's registry: every open loop with an owner and the exact proof that closes it. Codex reads it for state; Codex never edits it. Closures are Corvin's, on proof.
- **README.md** holds the setup state (config, login wall, workspace layout) and the packet format in full: what a packet carries and what a handback contains, including the fixed validation standard.
- **packets/** holds task packets, one Markdown file each. A packet is a complete, self-contained work order: objective, exact base, exact spec, acceptance proof named up front, boundaries, guardrails, handback list. The pilot packet, FLM-V2-PILOT-001, is the reference example of the form.
- **docs/** is out of scope for this lane: the pre-claw line's motion profile spec, tuning log, and v12 to v14 change notes for the old vex_his series. Codex never reads it. Nothing in it is a source.
- **runs/<packet-id>/** is the envelope a run works inside: `input/` holds staged copies of the base files (named in the packet; the originals are never the working surface), `work/` is scratch, `output/` receives candidate files, `report/` receives the validation report with raw outputs, and `LOG.md` is the run log per `PROCEDURE.md`. On the cloud route the envelope translates: the base is a repo commit, the workspace is the cloud task's, and the handback arrives as a diff; the contents required are the same.

## Scratch and reference (build/)

- **build/** is working scratch from past builds plus reference files, including `cadens_code.v5python` (the wiring scaffold the current device map came from) and its extracted `cadens_code_full.py`. Reference only: the wiring truth it carried now lives in the delivered code and in `CONTEXT.md`. Nothing in build/ is a deliverable and nothing there outranks a delivered version.

## How it connects, in one pass

Thunder's intent becomes a packet (Corvin). The packet names a base version from the claw series (or, later, a PROS base) and stages it into a run envelope. Codex executes inside the envelope and hands back candidates plus raw proof. Corvin verifies against the acceptance proof and the registry, delivers to Thunder, and only Thunder's gates move anything to Drive, to the repo's main line, or onto the robot. The research file informs movement packets; the protocol governs PROS packets; the registry tracks every open loop across all of it.
