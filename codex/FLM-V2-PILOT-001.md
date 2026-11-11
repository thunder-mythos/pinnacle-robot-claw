# Packet FLM-V2-PILOT-001: Reproduce claw_v18 from a Written Spec

- **Status:** Ready to fire. Blocked only on the repo import merge and the cloud environment publish.
- **Type:** First pilot for the FLM-V2 Codex worker (Robotics Code Work lane).
- **Model and effort (Thunder's policy, Nov 11, 2026):** Terra, Medium. Never Low; Medium is the minimum.
- **Run directory:** `~/workspace/robotics-fresh/codex/runs/FLM-V2-PILOT-001/`
- **Base (cloud re-aim):** after PR #1 merges, the base becomes commit afe2122 in thunder-mythos/pinnacle-robot-claw (`claw/claw_v17.py`, `claw/claw_v17.v5python`); the hash-pinned staged copies below stay the verification reference.

## Objective

Starting from claw_v17, produce claw_v18 by applying exactly one written spec change and regenerating the VEXcode wrapper, then prove the result matches the known-correct v18 exactly. This pilot tests the full handoff shape (spec in, patch plus validation report out) against a ground truth that already exists.

## Base (staged in `input/`, hash-pinned)

- `input/claw_v17.py` — SHA-256 `0bc94ad6c66595ae2b0b2ff158358e8d41aeba14374707dbf47e9eb83bd0bf9d`
- `input/claw_v17.v5python` — SHA-256 `258f4c6db7032d84f9cebbca8a26f2c493210e42c908cb7c017b213f42748875`

Verify both hashes before starting. If either differs, stop and report; do not proceed on a different base.

## Spec (the entire change)

1. In the code, set `DEFENSE_RETURN_VEL` to `40.0` (from `60.0`). This is the only value that changes. Nothing else in the file changes: no other constant, function, comment, or line.
2. Name the outputs `claw_v18.py` and `claw_v18.v5python`.
3. Build the wrapper from the patched .py by the fixed recipe: the .v5python is one-line JSON with compact separators; textContent is the wrapper region block from the base wrapper, then two newlines, then the .py body after the single console-clear line. The body must not redefine brain, controller, or any device; the IMU stays defined in the body, never in robotConfig. robotConfig stays at 11 devices, identical to base.

## Procedure

1. Copy `input/` files into `work/` and do all editing there.
2. Apply the spec change to the .py.
3. Generate the .v5python by the recipe.
4. Run the validation standard (below) and write the full results, raw, to `report/validation.md`, including the complete unified diff of both outputs against the base inputs.
5. Place the final `claw_v18.py` and `claw_v18.v5python` in `output/`.

## Acceptance proof (named up front, pass or fail)

The Robotics Code Work chat verifies after the run, against reference files held outside this run directory:

- `output/claw_v18.py` is byte-identical to the known claw_v18.py (SHA-256 `958a6504fd43d0a80be0408be68e77ab899cdaf63a370d1a827992b80cc5750c`).
- `output/claw_v18.v5python` is byte-identical to the known claw_v18.v5python (SHA-256 `7f32290fc9168f6d62dd6c87b5a7bff947691ae634854397d1e180060125f231`).
- The diff against base is exactly one line in each file: `DEFENSE_RETURN_VEL = 60.0` becomes `DEFENSE_RETURN_VEL = 40.0`, in the .py and at the same spot inside the wrapper textContent.
- Validation standard on both outputs: ast.parse clean, no duplicate top-level defs, exactly one `imu = Inertial`, exactly one `#endregion`, robotConfig count 11.

Any byte or content difference from the reference pair is a fail and gets reported line by line. There is no partial pass.

## Boundaries and blast radius

- Work only inside this run directory. Read only `input/`; write only `work/`, `output/`, and `report/`.
- Do not touch anything under `~/workspace/robotics-fresh/` outside this run directory. Do not touch Drive or GitHub. No network pushes of any kind.
- Do not change any other value, rename anything, or improve anything. This is a reproduction task, not a review.
- If anything in the spec is ambiguous, stop and write the question in the report instead of guessing.

## Guardrails

- Per-motor factors are scales, not caps.
- Drive torque stays at 100; slowing is done by speed alone, never by cutting torque.
- Every new tune variable is labeled UNTESTED or MATH-VERIFIED with its dependencies named, and is treated as wrong until it is manually tested, tuned, and confirmed on hardware, or it is mathematically correct with everything it relies on verified. (This pilot introduces no new variables; DEFENSE_RETURN_VEL at 40.0 is Thunder's ordered value from Nov 7, carried as UNTESTED on hardware like every defense value.)
- No claim about drive direction, snap turns, or heading hold until the by-hand IMU heading check and the wheels-up test pass. This pilot makes no hardware claim of any kind.
- The PROS switch is undecided; this pilot is VEXcode Python only and assumes nothing about PROS.
- Codex never chooses values, never decides version numbers or pushes, never makes a hardware claim, and never contacts Thunder directly.
- v17, v18, and Drive are untouched by this run; the reference v18 files stay exactly where they are and serve only as the verifier's answer key.

## Handback

- `output/claw_v18.py` and `output/claw_v18.v5python`
- `report/validation.md` with: the base hash verification, the full unified diff against base for both files, and the raw output of every validation check, pass or fail stated plainly.
- Open questions, if any, at the end of the report.
