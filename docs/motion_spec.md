# VEX robot motion profiles

**Model:** claude-sonnet-5-5

### User

### Recommend a mathematical motion profile for this use case.
**Object:** VEX Comp. Robot. Control variable: steering/turning. 
**Primary objective:** maximum smoothness, minimal jolting, & precision rotation. 

Compare suitable curves, equations, and implementation considerations.

---

### Recommend a mathematical motion profile for this use case.
**Object:** VEX Comp. Robot. Control variable: forward/backward driving. 
**Primary objective:** reaching maximum speed, minimal jolting, & precision.

Compare suitable curves, equations, and implementation considerations.

---

### Assistant

<details>
<summary>Smoothing trapezoid profiles into jerk-limited curves with code.</summary>



</details>

<br>

# 1. Turning (heading control)

**Priority:** smoothness and precision over speed.

| Profile | Equation (τ = t/T) | Peak ω | Peak α | Jerk | Verdict |
|---|---|---|---|---|---|
| Trapezoidal velocity | constant α, cruise, constant −α | set by you | set by you | **Impulses** at corners | Jolts at phase edges |
| Smoothstep (cubic) | θ = θ₀ + Δθ(3τ² − 2τ³) | 1.5Δθ/T | 6Δθ/T² | α jumps at start and end | Better, but still a small jolt |
| **Minimum-jerk (quintic)** | θ = θ₀ + Δθ(10τ³ − 15τ⁴ + 6τ⁵) | 1.875Δθ/T | 5.77Δθ/T² | Continuous. Zero velocity and acceleration at both ends | **Recommended** |
| S-curve (7-phase) | Piecewise jerk ±j | at cap | at cap | Bounded, with a cruise phase | Use for large turns (>~90°) at a velocity cap |
| P-only / exponential | ω = Kp·e | at start | at start | Peak jerk at t=0 | Jolts at start and is slow near the end |

**Recommendation:** use a quintic reference with closed-loop tracking.

- Duration: `T = max(1.875·Δθ/ω_max, sqrt(5.77·Δθ/α_max))`
- Each loop, compute θ_ref(t), ω_ref(t), α_ref(t).
- Control: `u = kV·ω_ref + kA·α_ref + kS·sign(ω_ref) + PID(θ_ref − θ_meas)`
- Add a small Kd on the heading error to damp the final settle.

**Implementation notes**
- Measure heading with the **inertial sensor**, not wheel encoders. Wheel slip during pivots makes encoder heading unreliable.
- Wait for sensor calibration to finish before moving.
- Wrap the error to ±180° so the robot takes the shortest path.
- Left and right get equal and opposite commands for a point turn.
- Exit when |error| < tol (~0.5–1°) **and** |ω| < ε for N consecutive loops, with a timeout.
- Run at a fixed 10 ms loop.

```python
def quintic(tau):          # returns position fraction, velocity fraction
    s = 10*tau**3 - 15*tau**4 + 6*tau**5
    v = 30*tau**2 - 60*tau**3 + 30*tau**4
    return s, v

# each loop: tau = min(t/T, 1); s, v = quintic(tau)
# theta_ref = th0 + dth*s ; omega_ref = dth*v/T
```

---

# 2. Driving (forward/backward)

**Priority:** reach top speed fast, with minimal jolt and precise stopping.

Min-jerk has no cruise phase, so its peak speed is only 1.875× the average. For max speed, use a cruise-capable profile.

| Profile | Shape | Jerk | Verdict |
|---|---|---|---|
| Trapezoidal velocity | ramp, cruise, ramp | Impulses at 4 corners | Fastest to implement, but jolts |
| **S-curve (jerk-limited trapezoid)** | rounded corners, cruise | Bounded | **Recommended** |
| Quintic / min-jerk | no cruise | Smoothest | Best for short moves (<~24") where you never reach vmax anyway |
| Slew-rate limiter on voltage | ramps the command | Bounded at start | Simple fallback, no position precision |

**Trapezoid equations** (distance d, accel a, cap v_max):
- Peak speed: `v_p = min(v_max, sqrt(a·d))` (triangular if d < v_max²/a)
- `t_a = v_p/a`, `t_c = (d − v_p·t_a)/v_p`, `T = 2t_a + t_c`
- Stopping distance at speed v: `v²/(2a)`

**S-curve via smoothing:** run the trapezoid velocity through a moving average of width `T_j = a/j_max`.
- The area (distance) is preserved.
- Jerk becomes `a/T_j`.
- Total time grows by `T_j`.
- This is much easier than the 7-phase piecewise form.

```python
def drive_profile(d, vmax, a, jmax, dt=0.01):
    vp = min(vmax, (a*d)**0.5)
    ta = vp/a; T = 2*ta + (d - vp*ta)/vp
    v = [min(a*i*dt, vp, a*(T - i*dt)) for i in range(int(T/dt)+1)]
    w = max(1, round(a/(jmax*dt)))
    pad = [0]*(w-1) + v + [0]*(w-1)
    return [sum(pad[i:i+w])/w for i in range(len(v)+w-1)]
# integrate to get x_ref[i]; feed v_ref[i], a_ref[i] to controller
```

**Control law (per loop):**
`volts = kV·v_ref + kA·a_ref + kS·sign(v_ref) + Kp·(x_ref − x) + Kd·(v_ref − v)`
- Add a **heading-hold PID** on the inertial sensor: `±Kh·(θ_target − θ)` applied differentially.
- Feedforward does most of the work. PID only corrects residual error.

**Implementation notes**
- **Max a is traction-limited:** `a ≤ μg` (rubber on foam tiles μ ≈ 0.8–1.0). In practice use 50–70% of this, and check the robot doesn't tip or pop a wheelie on decel if the CG is high.
- **v_max** = motor free speed × gear ratio × wheel circumference. Cap at ~85–90% so there is headroom for control.
- Use **voltage control** (`spin(FORWARD, volts, VOLT)`) so kV/kA/kS feedforward works as written. Velocity-mode control adds the motor's internal PID on top and can fight yours.
- Convert encoder units to inches: `dist = rev · π · D_wheel · gear_ratio`. Average left and right sides.
- Fit kV, kS, kA from characterization runs: step voltage, measure steady-state speed and initial accel.
- Make deceleration slightly gentler than accel if the robot carries game objects or has a high CG.
- Stop condition: |x_err| < tol (~0.25") **and** |v| < ε for N loops, then hold in brake mode. Always include a timeout.
- Use the same 10 ms loop and the same sensor-wait procedure as for turning.

---

**Summary:** quintic min-jerk for turns, S-curve (smoothed trapezoid) for drives. Both use feedforward plus PID tracking and an inertial sensor for heading.

---

### User

**What I want you to do rn is not worry at all about implementation and focus solely on getting the optimal form of movement here. **

For driving, we're currently using a 6 motor drive train (66watts, which is massive) so I want to start and end with precision (obviously) but joysticks also help with that, the real unlock would be to be able to "unlock" the max 66 when needed in a game through a moment of sustained driving, but also have precision when trying to score.

Similar for turning but we don't need to go that high, start much lower for precision scoring, which is much harder when it come to turning, but also be able to make tight 90 or 180 degree turns in game when necessary. 
Maybe for this we have a precision hold on the controller like some gaming mice have where it'll set the "DPI" much lower whilest the button is held, then it can go back up, but also incorporating a curve to support all of this...

---

### Assistant

<details>
<summary>Tuning response speed against traction and stability limits.</summary>



</details>

<br>

# Driver-control motion design

Split it into three independent layers. Each one solves a different problem, which is why a single curve can't do it all.

| Layer | Question it answers | Mechanism |
|---|---|---|
| **Shape** | What does stick position mean? | Expo curve |
| **Range** | How fast can "full stick" go right now? | Ceiling `L` (auto-unlock plus precision hold) |
| **Dynamics** | How does the robot get there and stop? | Critically damped S-curve shaper |

Keeping shape fixed while only the range changes is the key. The stick feels the same in every mode, so muscle memory carries over.

Your precision-hold idea is the right one: it's a sniper-button DPI drop on the range layer. The addition is that the ceiling also **unlocks automatically** when you commit to a long stroke, so you never manage it manually.

---

## 1. Shape (both axes)

After the deadband, `x = sgn(r)·(|r| − d)/(1 − d)`:

`f(x) = sgn(x)·[(1−k)|x| + k|x|³]`

Linear at the edges of the range, flat near center. A steeper cubic term gives more resolution where scoring happens. Use a higher `k` for turning than driving, since fine angular resolution is the harder problem.

## 2. Range (ceiling)

`target = P · L · f(x) · max`

**Auto-unlock.** `L` rises from a base `L₀` to 1 with **progress made during the current full-deflection stroke**:

`L = L₀ + (1 − L₀)·S(s/s_u)`, where `S(q) = 3q² − 2q³` (clamped to 0..1)

- Drive: `s` is the distance traveled. Turn: `s` is the angle swept.
- A stroke starts when `|f| > 0.85` and ends when `|f| < 0.6` (hysteresis).
- Progress is better than elapsed time here. A 90° turn takes about a third of a second, so a dwell timer would never fire. Progress also ties the unlock to intent: you only get max speed when you've actually committed to a long move or a big rotation.
- `L` falls back to `L₀` on a short time constant (~0.1 s) after the stroke ends.

**Precision hold.** `P` goes from 1 to ~0.3 (drive) and ~0.25 (turn) while held.
- Hold, not toggle, so there's no mode confusion.
- Auto-unlock is disabled while held.
- Lower `k` to ~0.35 while held, since the scale already provides fineness and a heavy cubic feels dead.
- `P` feeds the shaper directly, so no separate smoothing is needed.

## 3. Dynamics (the shaper)

Second-order critically damped response toward the target:

`v̈ + 2ωₙ·v̇ + ωₙ²·v = ωₙ²·v*`

- No overshoot, continuous acceleration, and S-shaped starts and stops.
- Stopping distance from speed `v` is exactly `2v/ωₙ`. It's linear in speed, so the driver learns it quickly. Precision mode stops short automatically.
- **Soft-limit** `|v̇|` to what the robot can physically deliver: `a_lim(v) = min(κ·μg, a_m·(1 − |v|/v_free))`. Traction caps low-speed launches, and motor back-EMF caps high-speed acceleration. Following this envelope gets you to top speed about as fast as physics allows without wheel slip.
- Braking cap: `min(κ_b·μg, g·d/h)`, where `d/h` is the CG-to-contact horizontal distance over CG height (the tip limit). Use `ωₙ_down ≈ 1.5–2× ωₙ_up` so stops are crisper than starts.
- Static friction offset: add `kS` to any nonzero output so the lowest precision range isn't a dead zone.

## 4. Turning-specific

- **Speed-dependent authority.** `|ω*| ≤ a_lat/|v|`. At standstill you get full pivot rate for 90s and 180s. At speed, turn rate falls off automatically, so arcs stay stable and nothing spins out or tips.
- **Turn priority at saturation.** If `v ± ω·b/2` exceeds `v_free` on either side, reduce forward speed rather than clipping the turn. Otherwise steering authority vanishes mid-boost.
- A lower turn base (`L₀ ≈ 0.4`) combined with a small `s_u` (~25°) gives precise nudges by default and a fast ramp to full rate for big rotations.

## Starting values (tune to your measured `v_max` and `ω_max`)

| Parameter | Drive | Turn |
|---|---|---|
| Deadband `d` | 0.06 | 0.08 |
| Expo `k` (normal / precision) | 0.55 / 0.35 | 0.75 / 0.4 |
| Base ceiling `L₀` | 0.65 | 0.40 |
| Unlock progress `s_u` | ~18" | ~25° |
| Precision scale `P` | 0.30 | 0.25 |
| `ωₙ` (up) | 15–20 rad/s | 15–20 rad/s |

## Optional extras

- **Heading hold.** When the turn stick is neutral and drive is active, lock to the current gyro heading so straight lines stay straight.
- **Snap-turn button.** A one-press 90°/180° using the quintic profile from earlier gives repeatable big rotations when you want zero variance. The stick-based unlock above covers the same need continuously.

## Why not the alternatives

| Alternative | Problem |
|---|---|
| Linear/arcade | No fine resolution near center |
| Pure expo | Can't unlock full power without losing low-end precision |
| Top-of-throw boost | Stateless, so accidental. It also doesn't signal sustained intent |
| Time-dwell unlock | Fails on short turns, and the unlock varies with speed |

---

