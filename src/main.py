# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       viraa                                                        #
# 	Created:      10/15/2026, 10:06:25 PM                                       #
# 	Description:  Pinnacle claw bot - v17 (v12 snap turns + TURN_KD 0.02)  #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *
import urandom
import math

# Brain should be defined by default
brain = Brain()

# Robot configuration code
controller_1 = Controller(PRIMARY)
L1 = Motor(Ports.PORT8, GearSetting.RATIO_6_1, True)
L2 = Motor(Ports.PORT9, GearSetting.RATIO_6_1, True)
L3 = Motor(Ports.PORT10, GearSetting.RATIO_6_1, True)
R1 = Motor(Ports.PORT1, GearSetting.RATIO_6_1, False)
R3 = Motor(Ports.PORT3, GearSetting.RATIO_6_1, False)
LiftL1 = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)
LiftR1 = Motor(Ports.PORT5, GearSetting.RATIO_18_1, True)
PneumaticClaw = DigitalOut(brain.three_wire_port.g)
RearSpinner = Motor(Ports.PORT21, GearSetting.RATIO_18_1, False)
PneumaticTilt = DigitalOut(brain.three_wire_port.f)
PuematicRotate = DigitalOut(brain.three_wire_port.h)
R2 = Motor(Ports.PORT2, GearSetting.RATIO_6_1, False)
LiftL2 = Motor(Ports.PORT7, GearSetting.RATIO_18_1, False)
LiftR2 = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)


# wait for rotation sensor to fully initialize
wait(30, MSEC)


# Make random actually random
def initializeRandomSeed():
    wait(100, MSEC)
    random = brain.battery.voltage(MV) + brain.battery.current(CurrentUnits.AMP) * 100 + brain.timer.system_high_res()
    urandom.seed(int(random))
      
# Set random seed 
initializeRandomSeed()


def play_vexcode_sound(sound_name):
    # Helper to make playing sounds from the V5 in VEXcode easier and
    # keeps the code cleaner by making it clear what is happening.
    print("VEXPlaySound:" + sound_name)
    wait(5, MSEC)

# add a small delay to make sure we don't print in the middle of the REPL header
wait(200, MSEC)
# clear the console to make sure we don't have the REPL in the console
print("\033[2J")

screen_precision = 0
console_precision = 0
controller_1_precision = 0
pneumaticClaw = True  # starts True so the FIRST B press fires (claw output starts False on power-up)
pneumaticRotate = False
puematicTilt = False
SpeedLeft = 0
SpeedRight = 0
MaxSpeed = 0

# ======================= EDIT THESE (all tuning lives here) =======================
# v12: every number you tune is in this one block. Each value says where it came from:
#   [YOU]   = you measured / told me     [SPEC] = your motion-profile spec (starting value)
#   [MATH]  = calculated from other values here      [v11] = unchanged from your v11
#   [GUESS] = NOT in the spec, a safe starting guess. Tune it, then change the tag to [YOU].

# ---------- master switches ----------
USE_NEW_DRIVE = True          # True = v12 driver pipeline (expo, unlock, precision, shaper, heading hold, snaps). False = your exact v11 arcade mapping.
USE_NEW_AUTON = True          # True = auton moves use S-curve drives + IMU quintic turns. False = your v11 spin_for moves (no IMU).
AUTON_TEST = "NONE"           # "NONE" = run the real auton. "DRIVE24" = auton only drives 24 in and prints the result. "TURN90" = auton only turns 90 right and prints the IMU heading.
                              # v13: "TUNE" = drive 24, turn 90, turn -90, drive -24, printing distance + heading error after each (PID tuning).
KEEP_R2_SPINNER = False       # [YOU] R2 is now precision/Fn. True brings back v11's R2 = spin RearSpinner FORWARD (it will ALSO trigger precision/Fn).

# ======================= TUNING - edit here (v13: every PID knob in one place) =======================
# Field tuning: set AUTON_TEST = "TUNE", run auton, read the errors on the controller/brain, change ONE number, repeat.
# Order: TURN_KP -> TURN_KD, then DRIVE_KP -> DRIVE_KD, then DRIVE_HEADING_KP. (Full plan in v13_PID_and_Tuning.pdf.)
# How both PIDs work: volts = kV*v_ref + kA*a_ref + kS + kP*(position error) + kD*(speed error)
#   kV/kA/kS (feedforward, below in CONFIG) do most of the work; kP/kD only clean up what's left.
# ---- drive (auton_drive: S-curve on averaged drive encoders) ----
DRIVE_KP = 0.8                # [GUESS] volts per inch behind/ahead. Raise: holds the planned path tighter, finishes closer. Too high: buzzes / rocks at the end.
DRIVE_KD = 0.05               # [GUESS] volts per in/s of speed error. Raise: damps the rock/overshoot at the stop. Too high: jittery.
DRIVE_HEADING_KP = 0.15       # [GUESS] volts per degree off-heading while driving. Raise: drives straighter. Too high: wiggles side to side.
DRIVE_HEADING_MAX_V = 3.0     # [GUESS] cap on heading correction volts. Raise only if it still drifts with a high DRIVE_HEADING_KP.
DRIVE_TOL_IN = 0.25           # [SPEC] "done" when within this many inches ... Lower: more accurate, slower to finish.
DRIVE_SETTLE_SPEED = 1.0      # [GUESS] ... and slower than this (in/s). Lower: waits for a fuller stop.
DRIVE_DISTANCE_SCALE = 1.116  # [YOU] DRIVE24 test went 21.5 in for 24 commanded: 24 / 21.5 = 1.116. Encoder inches are divided by this so commanded inches = real inches. 1.0 = off.
# ---- turn (auton_turn + snaps: quintic turn on the IMU) ----
TURN_KP = 0.25                # [GUESS] volts per degree of heading error. Raise: snappier, finishes the last degrees. Too high: overshoots / wobbles.
TURN_KI = 0.0                 # [GUESS] off. Only acts after the turn profile ends. Raise a tiny bit (0.01) ONLY if turns always stop 1-2 deg short.
TURN_KD = 0.02                # [YOU] v17: back to v12's 0.02 (0.03 undershot in the Oct 16 TUNE test). Volts per deg/s. Raise: kills wobble/overshoot at the end. Too high: sluggish or buzzy.
TURN_TOL_DEG = 1.0            # [SPEC] turn "done" within this many degrees (0.5-1). Lower: more accurate, slower.
TURN_SETTLE_DPS = 5.0         # [GUESS] ... and turning slower than this (deg/s).
# ---- shared ----
SETTLE_LOOPS = 5              # [GUESS] must be "done" this many 10 ms loops in a row (drives and turns). Raise: surer stop, slower.
SETTLE_MARGIN_SEC = 0.5       # [GUESS] timeout = planned move time + this. A stuck move gives up after this, so auton keeps going.
# ======================================================================================================

# ---------- BUTTONS (names: "A","B","X","Y","Up","Down","Left","Right","L1","L2","R1","R2") ----------
PRECISION_BUTTON = "R2"       # [YOU] HOLD for precision ("DPI drop")
FN_BUTTON = "R2"              # [YOU] HOLD = function key: changes what the arrow buttons do (can be split from precision later)
FN_SNAP_LEFT = "Left"         # [YOU] Fn + Left  = snap 90 left
FN_SNAP_RIGHT = "Right"       # [YOU] Fn + Right = snap 90 right
FN_MACRO_UP = "Up"            # [YOU] Fn + Up    = macro_up()   (stub, define it later)
FN_MACRO_DOWN = "Down"        # [YOU] Fn + Down  = macro_down() (stub). Down WITHOUT Fn still toggles claw rotate like v11.
# Unchanged from v11: L1 lift up, L2 lift down, R1 spinner, B claw, Y tilt, X lift coast 1 s, Down rotate. A is unbound.

AUTON_SIDE = "RIGHT"          # [v11] "LEFT" or "RIGHT": which way BOTH auton turns go

# ---------- robot geometry ----------
WHEEL_DIAMETER = 3.25         # [YOU] drive wheel diameter, inches (v11 had 2.75, wrong)
DRIVE_GEAR_RATIO = 0.75       # [YOU] wheel turns per motor turn: 36T on motor -> 48T on wheel = 36/48 = 0.75 ("yes for now, may change")
TRACK_WIDTH = 10.0            # [YOU] center of left wheels to center of right wheels, inches
MOTOR_FREE_RPM = 600          # [YOU] blue 6:1 cartridge
ROBOT_WEIGHT_LB = 15.0        # [GUESS] weigh the robot. Only used to estimate A_MOTOR and KA below.
CG_TIP_RATIO = 1.0            # [GUESS] d/h for the braking tip limit: horizontal CG-to-wheel-contact distance / CG height. Measure it (lift down).

# v_free = 600 rpm x 0.75 x pi x 3.25 in / 60 = 76.6 in/s (spec: motor free speed x gear ratio x wheel circumference)
V_FREE = MOTOR_FREE_RPM * DRIVE_GEAR_RATIO * math.pi * WHEEL_DIAMETER / 60.0          # [MATH] in/s, ~76.6
TURN_FREE_DPS = (2.0 * V_FREE / TRACK_WIDTH) * 180.0 / math.pi                        # [MATH] pivot rate if no wheel scrub, ~878 deg/s

# ---------- traction / acceleration (spec section 3) ----------
G_IN_S2 = 386.09              # gravity, in/s^2
MU = 0.9                      # [SPEC] rubber on foam tiles 0.8-1.0, middle value
KAPPA = 0.6                   # [SPEC] "use 50-70% of mu*g", middle value (acceleration)
KAPPA_BRAKE = 0.6             # [SPEC] kappa_b (spec gives no separate number, same as KAPPA)
# a_m = acceleration the motors give at 0 speed: 6 motors x 0.35 N*m (blue stall torque) / 0.75 gearing / 1.625 in wheel radius / robot mass
A_MOTOR = (6 * 0.35 / DRIVE_GEAR_RATIO / (WHEEL_DIAMETER / 2 * 0.0254)) / (ROBOT_WEIGHT_LB * 0.4536) / 0.0254   # [MATH] in/s^2, ~392 at 15 lb
A_TRACTION = KAPPA * MU * G_IN_S2                                                       # [MATH] ~208 in/s^2
A_BRAKE = min(KAPPA_BRAKE * MU * G_IN_S2, G_IN_S2 * CG_TIP_RATIO)                       # [MATH] spec braking cap min(kappa_b*mu*g, g*d/h)
A_LAT = KAPPA * MU * G_IN_S2  # [GUESS] lateral accel limit for turn authority |w*| <= a_lat/|v| (spec gives no number; same traction budget)

# ---------- feedforward (volts) ----------
KV = 12.0 / V_FREE            # [MATH] volts per in/s (12 V = free speed). Replace with characterization (spec: step voltage, measure speed).
KA = 12.0 / A_MOTOR           # [MATH] volts per in/s^2 (12 V = stall accel). Replace with characterization.
KS = 0.5                      # [GUESS] volts to just overcome friction. Find it: raise volts until the robot barely creeps.
KS_RAMP_IN_S = 1.0            # [GUESS] kS fades in over the first 1 in/s so it doesn't chatter around 0
TURN_FF_SCALE = 1.0           # [GUESS] extra turn feedforward for wheel scrub (pivots need more volts than ideal). Raise if turns lag.

# ---------- DRIVER: shape (spec section 1) ----------
DRIVE_DEADBAND = 0.06         # [SPEC] d, drive
TURN_DEADBAND = 0.08          # [SPEC] d, turn
DRIVE_EXPO = 0.55             # [SPEC] k, drive normal
TURN_EXPO = 0.75              # [SPEC] k, turn normal
DRIVE_EXPO_PRECISION = 0.35   # [SPEC] k, drive while precision held
TURN_EXPO_PRECISION = 0.40    # [SPEC] k, turn while precision held

# ---------- DRIVER: range ceiling L (spec section 2) ----------
DRIVE_L0 = 0.65               # [SPEC] base ceiling, drive
TURN_L0 = 0.55                # [YOU] base ceiling, turn (v12: 0.40 felt too slow). Moderate bump, ~1.4x, proportional to TURN_PRECISION's
DRIVE_UNLOCK_IN = 18.0        # [SPEC] s_u drive: inches of committed full-stick travel to reach 100%
TURN_UNLOCK_DEG = 25.0        # [SPEC] s_u turn: degrees of committed full-stick rotation to reach 100%
STROKE_START = 0.85           # [SPEC] |f| above this starts a full-deflection stroke
STROKE_END = 0.60             # [SPEC] |f| below this ends it
UNLOCK_FALL_TAU = 0.10        # [SPEC] seconds, L falls back to L0 after the stroke
DRIVER_DRIVE_MAX = V_FREE     # [MATH] "max" in target = P*L*f*max for drive (full 66 W when unlocked)
DRIVER_TURN_MAX = TURN_FREE_DPS  # [MATH] "max" for turn, deg/s

# ---------- DRIVER: precision hold (spec section 2) ----------
DRIVE_PRECISION = 0.30        # [SPEC] P drive while held (auto-unlock off, so drive max = 0.30 x 0.65 = 20%)
TURN_PRECISION = 0.35         # [YOU] P turn while held (v12: 0.25 -> Fn turn max 10%, didn't move). Now turn max = 0.35 x 0.55 = 19%

# ---------- DRIVER: shaper (spec section 3) ----------
WN_UP = 17.5                  # [SPEC] rad/s, 15-20 -> middle
WN_DOWN = 1.75 * WN_UP        # [SPEC] 1.5-2x WN_UP -> middle (stops crisper than starts)

# ---------- DRIVER: heading hold (spec extras) ----------
HEADING_HOLD = True           # [SPEC] lock to IMU heading when turn stick is centered and you're driving
HEADING_HOLD_KP = 4.0         # [GUESS] deg/s of correction per degree of heading error
HEADING_HOLD_MAX_DPS = 60.0   # [GUESS] cap on the correction
HEADING_CAPTURE_DPS = 10.0    # [GUESS] heading is locked once the robot's turn rate has died below this
HEADING_HOLD_MIN_SPEED = 2.0  # [GUESS] in/s, below this (and stick centered) hold is off

# ---------- SNAP TURNS (Fn + Left / Fn + Right) ----------
SNAP_DEG = 90                 # [YOU] snap size
SNAP_MAX_DPS = 350.0          # [YOU] v17: back to v12's 350 (v13-v16 had 250). Peak snap turn rate, same as auton turns
TURN_TRACTION_ACCEL_DPS2 = A_TRACTION / (TRACK_WIDTH / 2) * 180 / math.pi   # [MATH] traction-limited, ~2390 deg/s^2 (auton turns still use all of it)
SNAP_ACCEL_SCALE = 1.0        # [YOU] v17: back to v12 (full traction limit). v13-v16 had 0.6
SNAP_MAX_ACCEL_DPS2 = TURN_TRACTION_ACCEL_DPS2 * SNAP_ACCEL_SCALE        # [MATH] ~1430 deg/s^2

# ---------- AUTON: drives (spec section 2, S-curve) ----------
AUTON_DRIVE_SPEED = 25        # [v11] % speed for forward/backward moves in auton
AUTON_TURN_SPEED = AUTON_DRIVE_SPEED  # [v11] used only by USE_NEW_AUTON = False
AUTON_V_MAX = AUTON_DRIVE_SPEED / 100.0 * V_FREE   # [MATH] 25% of 76.6 = 19.1 in/s (same top speed as v11). Spec allows up to 85-90% of V_FREE.
AUTON_ACCEL = A_TRACTION      # [SPEC] 50-70% of mu*g
AUTON_JERK_TIME = 0.10        # [GUESS] T_j = a/j_max, seconds of corner rounding (spec gives the method, not the number)
# v13: DRIVE_KP, DRIVE_KD, DRIVE_HEADING_KP/MAX_V, DRIVE_TOL_IN, DRIVE_SETTLE_SPEED, SETTLE_LOOPS, SETTLE_MARGIN_SEC moved to TUNING at the top

# ---------- AUTON: turns (spec section 1, quintic) ----------
# Quintic peaks at 1.875x its average rate, so to keep the turn-around about as quick as v11 (~0.95 s)
# the peak must be ~1.875 x 180 / 0.97 s = ~350 deg/s.
AUTON_TURN_MAX_DPS = 350.0    # [GUESS/MATH] omega_max for T = max(1.875*dth/w_max, sqrt(5.77*dth/a_max))
AUTON_TURN_ACCEL_DPS2 = TURN_TRACTION_ACCEL_DPS2   # [MATH] alpha_max, traction-limited (v13: unchanged value; snaps alone got slower)
# v13: TURN_KP, TURN_KI, TURN_KD, TURN_TOL_DEG, TURN_SETTLE_DPS moved to TUNING at the top

# ---------- driver (USE_NEW_DRIVE = False only) ----------
DRIVER_DRIVE_SPEED = 0.6      # [v11] driver control: forward/backward = 60%
DRIVER_TURN_SPEED = 0.5       # [v11] driver control: turning = 50%
AUTON_PAUSE_MS = 800          # [v11] pause after every auton step, ms (auton must finish under 15 s)

# ---------- legacy turn conversion ----------
# v11: TURN_DEG_PER_ROBOT_DEG = 3.7, and Turn_side_robot_degrees(230) "turn around" = 230 x 3.7 = 851 drive MOTOR degrees.
#   Ideal math with the real numbers: 851 motor deg x 0.75 x pi x 3.25 in / 360 = 18.1 in per side;
#   18.1 in / (10 in / 2) = 3.62 rad = 207 deg. A pivot scrubs, so the real robot turns less than ideal:
#   your "turn around" label says it actually came out ~180. So 851 motor deg = 180 robot deg:
TURN_DEG_PER_ROBOT_DEG = 851.0 / 180.0   # [MATH] 4.73 drive motor degrees per robot degree (only used for v11-style turns and old motor-degree calls)

# ---------- lift ----------
LIFT_DEG_PER_INCH = 64        # [YOU] lift motor degrees per inch: measured 320 deg / 5 in (v12: 50 placeholder). Re-measure at low lift speed
LIFT_MAX_DEGREES = 900        # [v11] top limit, same 900 that driver control uses
LIFT_DOWN_SPEED = 50          # [v11] % speed for auton lift DOWN
LIFT_DRIVER_SPEED = 50        # [v11] % lift speed while L1/L2 is held (same 50 as v11)
LIFT_RAMP_SEC = 0.2           # [GUESS] v13: L1/L2 ramp the lift 0 -> 50% over this on press, and 50% -> 0 on release, THEN hold (no slam stop)

# ---------- tip guard (v13) ----------
TIP_GUARD_LIFT_DEG = 425      # [YOU] lift above this (LiftL1 degrees) = drive (forward/back) is capped. Turning is NOT capped
TIP_GUARD_DRIVE_SCALE = 0.50  # [YOU] drive gets 50% of its normal output while the guard is on
TIP_GUARD_RELEASE_DEG = 400   # [GUESS] guard turns off only once the lift is back below this (stops it flickering on/off right at 425)

# ---------- claw ----------
CLAW_CLOSED_OUTPUT = False    # [v11] PneumaticClaw value that CLOSES the claw

# ---------- IMU ----------
IMU_PORT = Ports.PORT15       # [YOU]

# ---------- safety ----------
DRIVE_MOVE_TIMEOUT_SEC = 3    # [v11] spin_for time limit (USE_NEW_AUTON = False)
LIFT_MOVE_TIMEOUT_SEC = 2     # [v11] same for lift moves
LOOP_MS = 10                  # [SPEC] fixed 10 ms control loop
# ========================================================================

def DriveTrain_Left_left_degrees(DriveTrain_Left_left_degrees__left_degrees):
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    # v12: amount is still drive motor degrees (same signature). New auton: IMU quintic turn of motor degrees / TURN_DEG_PER_ROBOT_DEG robot degrees.
    if USE_NEW_AUTON and imu_ok:
        auton_turn(-DriveTrain_Left_left_degrees__left_degrees / TURN_DEG_PER_ROBOT_DEG)
        return
    # turns LEFT: left side back, right side forward (was swapped before)
    L1.spin_for(REVERSE, DriveTrain_Left_left_degrees__left_degrees, DEGREES, wait=False)
    L2.spin_for(REVERSE, DriveTrain_Left_left_degrees__left_degrees, DEGREES, wait=False)
    L3.spin_for(REVERSE, DriveTrain_Left_left_degrees__left_degrees, DEGREES, wait=False)
    R1.spin_for(FORWARD, DriveTrain_Left_left_degrees__left_degrees, DEGREES, wait=False)
    R2.spin_for(FORWARD, DriveTrain_Left_left_degrees__left_degrees, DEGREES, wait=False)
    R3.spin_for(FORWARD, DriveTrain_Left_left_degrees__left_degrees, DEGREES, wait=True)

def DriveTrain_Right_right_degrees(DriveTrain_Right_right_degrees__right_degrees):
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    # v12: same signature (drive motor degrees). New auton: IMU quintic turn.
    if USE_NEW_AUTON and imu_ok:
        auton_turn(DriveTrain_Right_right_degrees__right_degrees / TURN_DEG_PER_ROBOT_DEG)
        return
    # turns RIGHT: left side forward, right side back (was swapped before)
    L1.spin_for(FORWARD, DriveTrain_Right_right_degrees__right_degrees, DEGREES, wait=False)
    L2.spin_for(FORWARD, DriveTrain_Right_right_degrees__right_degrees, DEGREES, wait=False)
    L3.spin_for(FORWARD, DriveTrain_Right_right_degrees__right_degrees, DEGREES, wait=False)
    R1.spin_for(REVERSE, DriveTrain_Right_right_degrees__right_degrees, DEGREES, wait=False)
    R2.spin_for(REVERSE, DriveTrain_Right_right_degrees__right_degrees, DEGREES, wait=False)
    R3.spin_for(REVERSE, DriveTrain_Right_right_degrees__right_degrees, DEGREES, wait=True)

def printdegrees():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    brain.screen.set_font(FontType.MONO40)
    brain.screen.clear_row(1)
    brain.screen.set_cursor(brain.screen.row(), 1)
    brain.screen.set_cursor(1, 1)
    brain.screen.print(LiftL1.position(DEGREES), precision=screen_precision)

def DriveTrain_Backward_back_degrees(DriveTrain_Backward_back_degrees__back_degrees):
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    # v12: same signature (drive motor degrees). New auton: S-curve drive backward.
    if USE_NEW_AUTON:
        auton_drive(-motor_deg_to_inches(DriveTrain_Backward_back_degrees__back_degrees))
        return
    L1.spin_for(REVERSE, DriveTrain_Backward_back_degrees__back_degrees, DEGREES, wait=False)
    L2.spin_for(REVERSE, DriveTrain_Backward_back_degrees__back_degrees, DEGREES, wait=False)
    L3.spin_for(REVERSE, DriveTrain_Backward_back_degrees__back_degrees, DEGREES, wait=False)
    R1.spin_for(REVERSE, DriveTrain_Backward_back_degrees__back_degrees, DEGREES, wait=False)
    R2.spin_for(REVERSE, DriveTrain_Backward_back_degrees__back_degrees, DEGREES, wait=False)
    R3.spin_for(REVERSE, DriveTrain_Backward_back_degrees__back_degrees, DEGREES, wait=True)  # wait=True: finish this move before the next

def DriveTrain_Forward_degrees(DriveTrain_Forward_degrees__degrees):
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    # v12: same signature (drive motor degrees). New auton: S-curve drive forward.
    if USE_NEW_AUTON:
        auton_drive(motor_deg_to_inches(DriveTrain_Forward_degrees__degrees))
        return
    L1.spin_for(FORWARD, DriveTrain_Forward_degrees__degrees, DEGREES, wait=False)
    L2.spin_for(FORWARD, DriveTrain_Forward_degrees__degrees, DEGREES, wait=False)
    L3.spin_for(FORWARD, DriveTrain_Forward_degrees__degrees, DEGREES, wait=False)
    R1.spin_for(FORWARD, DriveTrain_Forward_degrees__degrees, DEGREES, wait=False)
    R2.spin_for(FORWARD, DriveTrain_Forward_degrees__degrees, DEGREES, wait=False)
    R3.spin_for(FORWARD, DriveTrain_Forward_degrees__degrees, DEGREES, wait=True)  # wait=True: finish this move before the next

def clawOpenClose():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    if pneumaticClaw:
        PneumaticClaw.set(True)
        pneumaticClaw = False
    else:
        PneumaticClaw.set(False)
        pneumaticClaw = True

def clawRotate():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    if pneumaticRotate:
        PuematicRotate.set(True)
        pneumaticRotate = False
    else:
        PuematicRotate.set(False)
        pneumaticRotate = True

def lift_Down_degrees(lift_Down_degrees__degrees, wait_done=True):
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    printdegrees()
    LiftR1.set_velocity(LIFT_DOWN_SPEED, PERCENT)
    LiftL1.set_velocity(LIFT_DOWN_SPEED, PERCENT)
    LiftL2.set_velocity(LIFT_DOWN_SPEED, PERCENT)
    LiftR2.set_velocity(LIFT_DOWN_SPEED, PERCENT)
    # REVERSE = down (same as driver L2). Never go below 0 (the bottom).
    lift_Down_degrees__degrees = min(lift_Down_degrees__degrees, LiftL1.position(DEGREES))
    if lift_Down_degrees__degrees <= 0:
        return
    LiftL1.spin_for(REVERSE, lift_Down_degrees__degrees, DEGREES, wait=False)
    LiftR1.spin_for(REVERSE, lift_Down_degrees__degrees, DEGREES, wait=False)
    LiftL2.spin_for(REVERSE, lift_Down_degrees__degrees, DEGREES, wait=False)
    LiftR2.spin_for(REVERSE, lift_Down_degrees__degrees, DEGREES, wait=wait_done)   # v13: wait_done=False only for macros

def lift_Up_degrees(lift_Up_degrees__degrees, wait_done=True):
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    printdegrees()
    LiftR1.set_velocity(50, PERCENT)
    LiftL1.set_velocity(50, PERCENT)
    LiftL2.set_velocity(50, PERCENT)
    LiftR2.set_velocity(50, PERCENT)
    # FORWARD = up (same as driver L1). Never go above LIFT_MAX_DEGREES (900).
    lift_Up_degrees__degrees = min(lift_Up_degrees__degrees, LIFT_MAX_DEGREES - LiftL1.position(DEGREES))
    if lift_Up_degrees__degrees <= 0:
        return
    LiftL1.spin_for(FORWARD, lift_Up_degrees__degrees, DEGREES, wait=False)
    LiftR1.spin_for(FORWARD, lift_Up_degrees__degrees, DEGREES, wait=False)
    LiftL2.spin_for(FORWARD, lift_Up_degrees__degrees, DEGREES, wait=False)
    LiftR2.spin_for(FORWARD, lift_Up_degrees__degrees, DEGREES, wait=wait_done)   # v13: wait_done=False only for macros

# ----------------------- auton helpers (added) -----------------------
# You shouldn't need to edit these. The numbers they use are in EDIT THESE at the top.
DRIVE_MOTORS = [L1, L2, L3, R1, R2, R3]
LIFT_MOTORS = [LiftL1, LiftL2, LiftR1, LiftR2]
auton_start_ms = 0

def inches_to_degrees(inches):
    # wheel inches -> drive motor degrees. One wheel turn rolls pi x diameter inches.
    # v12 fix: DRIVE_GEAR_RATIO is now wheel turns per motor turn (0.75), so motor degrees = wheel degrees / 0.75
    # v13: x DRIVE_DISTANCE_SCALE (robot really rolls 1/1.116 of the ideal inches, so it needs more motor degrees)
    return inches / (math.pi * WHEEL_DIAMETER) * 360 / DRIVE_GEAR_RATIO * DRIVE_DISTANCE_SCALE

def robot_turn_to_degrees(robot_degrees):
    # how far the ROBOT turns -> drive motor degrees (v12: the new turn code divides this back out, so it's exact robot degrees on the IMU).
    return robot_degrees * TURN_DEG_PER_ROBOT_DEG

def lift_inches_to_degrees(inches):
    # lift height inches -> lift motor degrees (tune LIFT_DEG_PER_INCH)
    return inches * LIFT_DEG_PER_INCH

def set_drive_velocity(percent):
    for motor in DRIVE_MOTORS:
        motor.set_velocity(percent, PERCENT)

def DriveTrain_Turn_toward_side(DriveTrain_Turn_toward_side__degrees):
    # turns LEFT if AUTON_SIDE is "LEFT", RIGHT if it's "RIGHT" (amount is in drive motor degrees)
    set_drive_velocity(AUTON_TURN_SPEED)
    if AUTON_SIDE == "LEFT":
        DriveTrain_Left_left_degrees(DriveTrain_Turn_toward_side__degrees)
    else:
        DriveTrain_Right_right_degrees(DriveTrain_Turn_toward_side__degrees)
    set_drive_velocity(AUTON_DRIVE_SPEED)

def claw_set(closed):
    # claw_set(True) closes, claw_set(False) opens. Also updates the driver toggle flag,
    # so the first B press in driver control flips the claw instead of doing nothing.
    global pneumaticClaw
    if closed:
        output = CLAW_CLOSED_OUTPUT
    else:
        output = not CLAW_CLOSED_OUTPUT
    PneumaticClaw.set(output)
    pneumaticClaw = not output  # driver B sets True when this flag is True, so this makes the next press flip it

# ---- plain-number moves for the auton routine: type real inches / degrees straight in ----
def Forward_inches(inches):
    DriveTrain_Forward_degrees(inches_to_degrees(inches))

def Backward_inches(inches):
    DriveTrain_Backward_back_degrees(inches_to_degrees(inches))

def Turn_side_inches(inches):
    # small turn toward AUTON_SIDE, in inches of real wheel travel per side (v12: 1 in = 11.5 deg ideal: 1 / 5 in half-track = 0.2 rad)
    DriveTrain_Turn_toward_side(inches_to_degrees(inches))

def Turn_side_robot_degrees(robot_degrees):
    # turn the ROBOT this many degrees toward AUTON_SIDE (180 = turn around)
    DriveTrain_Turn_toward_side(robot_turn_to_degrees(robot_degrees))

def Lift_Up_inches(inches, wait_done=True):
    lift_Up_degrees(lift_inches_to_degrees(inches), wait_done)

def Lift_Down_inches(inches, wait_done=True):
    lift_Down_degrees(lift_inches_to_degrees(inches), wait_done)

def auton_setup():
    # runs first in auton: speeds, brake, time limits, and zero the lift (lift must START at the bottom)
    global auton_start_ms, auton_heading_target
    auton_start_ms = brain.timer.time(MSEC)
    auton_heading_target = imu_rot()   # v12: the way the robot faces at the start is "straight"
    for motor in DRIVE_MOTORS:
        motor.set_velocity(AUTON_DRIVE_SPEED, PERCENT)
        motor.set_stopping(BRAKE)
        motor.set_timeout(DRIVE_MOVE_TIMEOUT_SEC, SECONDS)
    for motor in LIFT_MOTORS:
        motor.set_position(0, DEGREES)
        motor.set_timeout(LIFT_MOVE_TIMEOUT_SEC, SECONDS)

def auton_finish():
    # runs last in auton: stop everything. Lift motors are on HOLD (when_started1), so the lift stays put.
    for motor in LIFT_MOTORS:
        motor.stop()
    for motor in DRIVE_MOTORS:
        motor.stop()
        motor.set_stopping(COAST)  # back to normal for driver control
    # show how long auton took (must be under 15 s)
    auton_seconds = (brain.timer.time(MSEC) - auton_start_ms) / 1000
    brain.screen.set_cursor(3, 1)
    brain.screen.print("Auton " + str(round(auton_seconds, 1)) + "s")
    print("Auton took " + str(round(auton_seconds, 1)) + " s")
# ---------------------------------------------------------------------

# ======================= v12 motion code (you shouldn't need to edit this; numbers are in the CONFIG block) =======================
imu = Inertial(IMU_PORT)
imu_ready = False      # True once calibration is finished; nothing drives before that
imu_ok = False         # True if the IMU is plugged in. If not, turns fall back to v11 motor-degree turns.
auton_heading_target = 0.0   # where auton thinks the robot SHOULD be pointing (IMU rotation, degrees)
snap_request = 0       # set by Fn + Left/Right (-90 / +90), picked up by the driver loop

def button_by_name(name):
    # "L2" -> controller_1.buttonL2. None stays None.
    if name is None:
        return None
    return getattr(controller_1, "button" + name)

precision_btn = button_by_name(PRECISION_BUTTON)
fn_btn = button_by_name(FN_BUTTON)

def sgn(x):
    if x > 0:
        return 1.0
    if x < 0:
        return -1.0
    return 0.0

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def wrap180(deg):
    # wrap an angle error to -180..180 so the robot takes the short way
    while deg > 180:
        deg -= 360
    while deg < -180:
        deg += 360
    return deg

def calibrate_imu():
    # Spec: wait for calibration to finish before moving. Keep the robot STILL for ~2 s.
    global imu_ready, imu_ok
    try:
        imu_ok = imu.installed()
    except Exception:
        imu_ok = True
    brain.screen.clear_screen()
    brain.screen.set_font(FontType.MONO20)
    brain.screen.set_cursor(1, 1)
    if not imu_ok:
        brain.screen.print("NO IMU on port 15!")
        print("NO IMU on port 15: heading hold/snaps off, auton turns use v11 motor degrees")
        imu_ready = True
        return
    brain.screen.print("IMU calibrating")
    imu.calibrate()
    wait(100, MSEC)
    while imu.is_calibrating():
        wait(50, MSEC)
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    brain.screen.print("IMU ready")
    imu_ready = True

def wait_for_imu():
    while not imu_ready:
        wait(20, MSEC)

def imu_rot():
    # continuous heading in degrees, clockwise (right turn) = positive. 0 if no IMU.
    if not imu_ok:
        return 0.0
    return imu.rotation(DEGREES)

# ---------- encoders (averaged), using the fixed wheel/gear numbers ----------
def motor_deg_to_inches(motor_degrees):
    # v13: / DRIVE_DISTANCE_SCALE = REAL inches (exact inverse of inches_to_degrees, so the scale is applied once, never twice)
    return motor_degrees / 360.0 * DRIVE_GEAR_RATIO * math.pi * WHEEL_DIAMETER / DRIVE_DISTANCE_SCALE

def drive_position_in():
    left = (L1.position(DEGREES) + L2.position(DEGREES) + L3.position(DEGREES)) / 3.0
    right = (R1.position(DEGREES) + R2.position(DEGREES) + R3.position(DEGREES)) / 3.0
    return motor_deg_to_inches((left + right) / 2.0)

def drive_speed_in_s():
    rpm = (L1.velocity(RPM) + L2.velocity(RPM) + L3.velocity(RPM) + R1.velocity(RPM) + R2.velocity(RPM) + R3.velocity(RPM)) / 6.0
    return rpm / 60.0 * DRIVE_GEAR_RATIO * math.pi * WHEEL_DIAMETER / DRIVE_DISTANCE_SCALE   # v13: real in/s, same units as drive_position_in()

# ---------- output (voltage control, spec) ----------
def set_drive_volts(left_v, right_v):
    left_v = clamp(left_v, -12.0, 12.0)
    right_v = clamp(right_v, -12.0, 12.0)
    L1.spin(FORWARD, left_v, VOLT)
    L2.spin(FORWARD, left_v, VOLT)
    L3.spin(FORWARD, left_v, VOLT)
    R1.spin(FORWARD, right_v, VOLT)
    R2.spin(FORWARD, right_v, VOLT)
    R3.spin(FORWARD, right_v, VOLT)

def stop_drive(mode):
    for motor in DRIVE_MOTORS:
        motor.stop(mode)

def ks_term(speed_in_s):
    # spec: add kS to any nonzero output (faded in over KS_RAMP_IN_S so it doesn't buzz at 0)
    return KS * clamp(speed_in_s / KS_RAMP_IN_S, -1.0, 1.0)

def side_ff_volts(speed_in_s, accel_in_s2):
    return KV * speed_in_s + KA * accel_in_s2 + ks_term(speed_in_s)

def dps_to_side(dps):
    # robot turn rate (deg/s) -> wheel speed each side needs (in/s): w * b/2
    return dps * math.pi / 180.0 * TRACK_WIDTH / 2.0

def side_to_dps(in_s):
    return in_s / (TRACK_WIDTH / 2.0) * 180.0 / math.pi

# ---------- spec section 1: deadband + expo ----------
def deadband(r, d):
    if abs(r) <= d:
        return 0.0
    return sgn(r) * (abs(r) - d) / (1.0 - d)

def expo(x, k):
    # f(x) = sgn(x) * [(1-k)|x| + k|x|^3]
    ax = abs(x)
    return sgn(x) * ((1.0 - k) * ax + k * ax * ax * ax)

def smoothstep(q):
    q = clamp(q, 0.0, 1.0)
    return 3.0 * q * q - 2.0 * q * q * q

# ---------- spec section 2: range ceiling with auto-unlock ----------
class Ceiling:
    def __init__(self, L0, s_u):
        self.L0 = L0
        self.s_u = s_u
        self.L = L0
        self.active = False
        self.start = 0.0

    def update(self, f, progress, precision, dt):
        # progress = encoder inches (drive) or IMU degrees (turn)
        if precision:
            self.active = False            # auto-unlock disabled while precision is held
        elif not self.active and abs(f) > STROKE_START:
            self.active = True
            self.start = progress
        elif self.active and abs(f) < STROKE_END:
            self.active = False
        if self.active:
            s = abs(progress - self.start)
            self.L = max(self.L, self.L0 + (1.0 - self.L0) * smoothstep(s / self.s_u))
        else:
            self.L += (self.L0 - self.L) * min(1.0, dt / UNLOCK_FALL_TAU)
        return self.L

# ---------- spec section 3: critically damped shaper with accel soft-limit ----------
class Shaper:
    # v'' + 2*wn*v' + wn^2*v = wn^2*v*   (no overshoot, S-shaped starts/stops)
    # |v'| soft-limited: accelerating a_lim(v) = min(a_trac, a_m*(1-|v|/v_free)); braking a_brake
    def __init__(self, a_trac, a_motor, a_brake, v_free):
        self.v = 0.0
        self.a = 0.0
        self.a_trac = a_trac
        self.a_motor = a_motor
        self.a_brake = a_brake
        self.v_free = v_free

    def reset(self, v):
        self.v = v
        self.a = 0.0

    def step(self, target, dt):
        v = self.v
        if abs(target) > abs(v) and target * v >= 0:
            wn = WN_UP
        else:
            wn = WN_DOWN
        a = self.a + (wn * wn * (target - v) - 2.0 * wn * self.a) * dt
        if v * a > 0 or abs(v) < 1e-6:
            lim = min(self.a_trac, self.a_motor * max(0.0, 1.0 - abs(v) / self.v_free))
        else:
            lim = self.a_brake
        a = clamp(a, -lim, lim)
        v_new = v + a * dt
        if (v - target) * (v_new - target) < 0:   # never cross the target (the limiter can't cause overshoot)
            v_new = target
            a = 0.0
        self.v = v_new
        self.a = a
        return self.v

# ---------- spec section 1: quintic min-jerk turn on the IMU (auton turns AND driver snaps) ----------
def quintic(tau):
    # position, velocity, acceleration fractions
    s = 10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5
    v = 30 * tau ** 2 - 60 * tau ** 3 + 30 * tau ** 4
    a = 60 * tau - 180 * tau ** 2 + 120 * tau ** 3
    return s, v, a

class QuinticTurn:
    # u = kV*w_ref + kA*a_ref + kS*sign(w_ref) + PID(theta_ref - theta)   (volts; + = turn right)
    def __init__(self, delta_deg, w_max, a_max):
        self.th0 = imu_rot()
        self.dth = delta_deg
        d = abs(delta_deg)
        self.T = max(1.875 * d / w_max, math.sqrt(5.77 * d / a_max), 0.05)
        self.t0 = brain.timer.time(MSEC)
        self.timeout = self.T + SETTLE_MARGIN_SEC
        self.last_rot = self.th0
        self.last_ms = self.t0
        self.integral = 0.0
        self.good_loops = 0
        self.w_ref = 0.0
        self.rate = 0.0

    def target(self):
        return self.th0 + self.dth

    def step(self):
        now = brain.timer.time(MSEC)
        t = (now - self.t0) / 1000.0
        dt = max(0.001, (now - self.last_ms) / 1000.0)
        tau = min(t / self.T, 1.0)
        s, vf, af = quintic(tau)
        th_ref = self.th0 + self.dth * s
        self.w_ref = self.dth * vf / self.T
        a_ref = self.dth * af / (self.T * self.T)
        rot = imu_rot()
        self.rate = (rot - self.last_rot) / dt
        self.last_rot = rot
        self.last_ms = now
        err = wrap180(th_ref - rot)
        if tau >= 1.0:
            self.integral = clamp(self.integral + err * dt, -20.0, 20.0)
        side_w = dps_to_side(self.w_ref)
        side_a = dps_to_side(a_ref)
        final_err = wrap180(self.target() - rot)
        ks = KS * sgn(self.w_ref)
        if tau >= 1.0 and abs(final_err) > TURN_TOL_DEG:
            ks = KS * sgn(final_err)      # settle: push past static friction so the PID can finish the last degree
        volts = TURN_FF_SCALE * (KV * side_w + KA * side_a) + ks \
            + TURN_KP * err + TURN_KI * self.integral + TURN_KD * (self.w_ref - self.rate)
        if tau >= 1.0 and abs(final_err) < TURN_TOL_DEG and abs(self.rate) < TURN_SETTLE_DPS:
            self.good_loops += 1
        else:
            self.good_loops = 0
        done = self.good_loops >= SETTLE_LOOPS or t > self.timeout
        return volts, done

# ---------- spec section 2: S-curve (smoothed trapezoid) drive ----------
def drive_profile(d, vmax, a, jerk_time, dt):
    # trapezoid, then moving average of width T_j: distance preserved, jerk bounded
    vp = min(vmax, math.sqrt(a * d))
    ta = vp / a
    T = 2 * ta + (d - vp * ta) / vp
    n = int(T / dt) + 1
    v = [max(0.0, min(a * i * dt, vp, a * (T - i * dt))) for i in range(n)]
    w = max(1, int(round(jerk_time / dt)))
    pad = [0.0] * (w - 1) + v + [0.0] * (w - 1)
    out = []
    run = 0.0
    for i in range(len(pad)):
        run += pad[i]
        if i >= w:
            run -= pad[i - w]
        if i >= w - 1:
            out.append(run / w)
    total = sum(out) * dt
    if total > 0:
        scale = d / total               # make the area exactly d inches
        out = [x * scale for x in out]
    return out

def auton_drive(inches):
    # S-curve on averaged encoders: volts = kV*v_ref + kA*a_ref + kS*sign + Kp*(x_ref - x) + Kd*(v_ref - v), plus IMU heading hold
    if abs(inches) < 0.05:
        return
    dt = LOOP_MS / 1000.0
    direction = sgn(inches)
    prof = drive_profile(abs(inches), AUTON_V_MAX, AUTON_ACCEL, AUTON_JERK_TIME, dt)
    n = len(prof)
    T = n * dt
    timeout = T + SETTLE_MARGIN_SEC
    x0 = drive_position_in()
    heading = auton_heading_target
    t0 = brain.timer.time(MSEC)
    x_ref = 0.0
    last_i = -1
    good = 0
    while True:
        t = (brain.timer.time(MSEC) - t0) / 1000.0
        i = int(t / dt)
        while last_i < min(i, n - 1):   # integrate the reference up to now
            last_i += 1
            x_ref += prof[last_i] * dt
        if i < n:
            v_ref = prof[i]
            a_ref = (prof[i] - prof[i - 1]) / dt if i > 0 else prof[0] / dt
        else:
            v_ref = 0.0
            a_ref = 0.0
            x_ref = abs(inches)
        x = (drive_position_in() - x0) * direction
        v = drive_speed_in_s() * direction
        ks = KS * sgn(v_ref)
        if i >= n and abs(abs(inches) - x) > DRIVE_TOL_IN:
            ks = KS * sgn(abs(inches) - x)   # settle: push past static friction so the PID can finish the last fraction of an inch
        volts = KV * v_ref + KA * a_ref + ks + DRIVE_KP * (x_ref - x) + DRIVE_KD * (v_ref - v)
        volts *= direction
        h = 0.0
        if imu_ok:
            h = clamp(DRIVE_HEADING_KP * wrap180(heading - imu_rot()), -DRIVE_HEADING_MAX_V, DRIVE_HEADING_MAX_V)
        set_drive_volts(volts + h, volts - h)
        if i >= n and abs(abs(inches) - x) < DRIVE_TOL_IN and abs(v) < DRIVE_SETTLE_SPEED:
            good += 1
        else:
            good = 0
        if good >= SETTLE_LOOPS or t > timeout:
            break
        if macro_cancelled():   # v13: driver cancelled a macro (always False in auton)
            break
        wait(LOOP_MS, MSEC)
    stop_drive(BRAKE)

def auton_turn(robot_degrees):
    # + = right (clockwise), - = left. Turns relative to where auton SHOULD be pointing, so small errors don't pile up.
    global auton_heading_target
    if not imu_ok:
        legacy_turn_motor_degrees(robot_degrees * TURN_DEG_PER_ROBOT_DEG)
        return
    delta = robot_degrees + wrap180(auton_heading_target - imu_rot())
    turn = QuinticTurn(delta, AUTON_TURN_MAX_DPS, AUTON_TURN_ACCEL_DPS2)
    while True:
        volts, done = turn.step()
        set_drive_volts(volts, -volts)
        if done:
            break
        if macro_cancelled():   # v13: driver cancelled a macro (always False in auton)
            break
        wait(LOOP_MS, MSEC)
    stop_drive(BRAKE)
    auton_heading_target = auton_heading_target + robot_degrees

def legacy_turn_motor_degrees(motor_degrees):
    # v11 open-loop turn (used only with no IMU or USE_NEW_AUTON = False). + = right.
    set_drive_velocity(AUTON_TURN_SPEED)
    if motor_degrees >= 0:
        DriveTrain_Right_right_degrees(motor_degrees)
    else:
        DriveTrain_Left_left_degrees(-motor_degrees)
    set_drive_velocity(AUTON_DRIVE_SPEED)

# ---------- driver: Fn key, snaps, macros ----------
# ---------- v13 macro framework ----------
# A macro is a list of steps run with the same proven moves auton uses:
#   ("drive", inches)       auton_drive: + forward, - backward (real inches)
#   ("turn", degrees)       auton_turn on the IMU: + right, - left, from where the robot points WHEN THE MACRO STARTS
#   ("lift_up", inches)     Lift_Up_inches       ("lift_down", inches)  Lift_Down_inches
#   ("claw", True/False)    claw_set: True closes, False opens
#   ("wait", ms)            pause
# CANCEL: move any stick past MACRO_CANCEL_STICK, or press Fn + the same arrow again -> everything stops.
MACRO_CANCEL_STICK = 0.20     # [GUESS] stick fraction (0-1) that cancels a running macro. Raise if stick drift cancels macros by itself.
macro_running = False         # True while a macro runs; the driver loop stays hands-off until it ends
macro_abort = False           # set when the driver cancels
macro_arrow = None            # the arrow button that started the running macro
macro_arrow_let_go = False    # the arrow must be released once before pressing it again counts as cancel

def macro_cancelled():
    # True if a macro is running and the driver wants out. Checked between steps and inside auton_drive/auton_turn loops.
    global macro_abort, macro_arrow_let_go
    if not macro_running:
        return False
    if macro_abort:
        return True
    for axis in (controller_1.axis1, controller_1.axis2, controller_1.axis3, controller_1.axis4):
        if abs(axis.position()) / 100.0 > MACRO_CANCEL_STICK:
            macro_abort = True
    if macro_arrow is not None:
        if not macro_arrow.pressing():
            macro_arrow_let_go = True
        elif macro_arrow_let_go and fn_held():
            macro_abort = True
    return macro_abort

def macro_wait(ms):
    # a wait that can be cancelled
    end = brain.timer.time(MSEC) + ms
    while brain.timer.time(MSEC) < end:
        if macro_cancelled():
            return
        wait(LOOP_MS, MSEC)

def macro_lift_wait():
    # wait for a lift move to finish (or the macro to be cancelled)
    end = brain.timer.time(MSEC) + LIFT_MOVE_TIMEOUT_SEC * 1000
    while brain.timer.time(MSEC) < end:
        if macro_cancelled():
            return
        if LiftL1.is_done() and LiftL2.is_done() and LiftR1.is_done() and LiftR2.is_done():
            return
        wait(LOOP_MS, MSEC)

def run_macro(name, arrow_name, steps):
    global macro_running, macro_abort, macro_arrow, macro_arrow_let_go, auton_heading_target
    if macro_running:
        macro_abort = True     # Fn + arrow while a macro runs = cancel it
        return
    controller_1.screen.clear_row(1)
    controller_1.screen.set_cursor(1, 1)
    if len(steps) == 0:
        controller_1.screen.print(name + ": empty")
        return
    macro_arrow = button_by_name(arrow_name)
    macro_arrow_let_go = False
    macro_abort = False
    macro_running = True
    controller_1.screen.print(name)
    auton_heading_target = imu_rot()   # turns are relative to where the driver left the robot pointing
    for motor in LIFT_MOTORS:
        motor.set_timeout(LIFT_MOVE_TIMEOUT_SEC, SECONDS)
    for step in steps:
        if macro_cancelled():
            break
        kind = step[0]
        amount = step[1]
        if kind == "drive":
            auton_drive(amount)
        elif kind == "turn":
            auton_turn(amount)
        elif kind == "lift_up":
            Lift_Up_inches(amount, False)
            macro_lift_wait()
        elif kind == "lift_down":
            Lift_Down_inches(amount, False)
            macro_lift_wait()
        elif kind == "claw":
            claw_set(amount)
        elif kind == "wait":
            macro_wait(amount)
    cancelled = macro_abort
    # stop everything: drive brakes, lift stops on HOLD (stays where it is)
    stop_drive(BRAKE)
    for motor in LIFT_MOTORS:
        motor.stop()
    controller_1.screen.clear_row(1)
    controller_1.screen.set_cursor(1, 1)
    if cancelled:
        controller_1.screen.print(name + " CANCEL")
    else:
        controller_1.screen.print(name + " done")
    macro_running = False

# Steps for each macro go in these lists. EMPTY until you decide what they do.
# Example (NOT active): close claw, lift up 6 in, back up 8 in, turn 90 right:
#   MACRO_UP_STEPS = [("claw", True), ("wait", 200), ("lift_up", 6), ("drive", -8), ("turn", 90)]
MACRO_UP_STEPS = []
MACRO_DOWN_STEPS = []

def macro_up():
    # DRIVER MACRO (Fn + Up): runs MACRO_UP_STEPS (empty for now)
    run_macro("macro_up", FN_MACRO_UP, MACRO_UP_STEPS)

def macro_down():
    # DRIVER MACRO (Fn + Down): runs MACRO_DOWN_STEPS (empty for now)
    run_macro("macro_down", FN_MACRO_DOWN, MACRO_DOWN_STEPS)

def fn_held():
    return fn_btn is not None and fn_btn.pressing()

def fn_arrow(name):
    # returns True if Fn was held and the arrow did its Fn job
    global snap_request
    if not fn_held():
        return False
    if name == FN_SNAP_LEFT:
        snap_request = -SNAP_DEG
    elif name == FN_SNAP_RIGHT:
        snap_request = SNAP_DEG
    elif name == FN_MACRO_UP:
        macro_up()
    elif name == FN_MACRO_DOWN:
        macro_down()
    return True

def controller_1buttonUp_pressed_callback_0():
    fn_arrow("Up")       # no v11 job without Fn

def controller_1buttonLeft_pressed_callback_0():
    fn_arrow("Left")     # no v11 job without Fn

def controller_1buttonRight_pressed_callback_0():
    fn_arrow("Right")    # no v11 job without Fn

def sticks_active():
    return abs(controller_1.axis3.position() / 100.0) > DRIVE_DEADBAND or abs(controller_1.axis1.position() / 100.0) > TURN_DEADBAND

# ---------- driver: the new pipeline (spec sections 1-4 + heading hold) ----------
def new_driver_loop():
    global snap_request
    wait_for_imu()
    snap_request = 0
    dt = LOOP_MS / 1000.0
    turn_a_trac = side_to_dps(A_TRACTION)
    turn_a_motor = side_to_dps(A_MOTOR)
    turn_a_brake = side_to_dps(A_BRAKE)
    drive_sh = Shaper(A_TRACTION, A_MOTOR, A_BRAKE, V_FREE)
    turn_sh = Shaper(turn_a_trac, turn_a_motor, turn_a_brake, TURN_FREE_DPS)
    drive_L = Ceiling(DRIVE_L0, DRIVE_UNLOCK_IN)
    turn_L = Ceiling(TURN_L0, TURN_UNLOCK_DEG)
    hold_target = None
    snap = None
    while True:
        if macro_running:
            # v13: a driver macro owns the motors; stay hands-off and restart smoothly from 0 when it ends
            drive_sh.reset(0.0)
            turn_sh.reset(0.0)
            hold_target = None
            snap = None
            snap_request = 0
            wait(LOOP_MS, MSEC)
            continue
        rd = controller_1.axis3.position() / 100.0
        rt = controller_1.axis1.position() / 100.0
        xd = deadband(rd, DRIVE_DEADBAND)
        xt = deadband(rt, TURN_DEADBAND)

        # ---- snap turns (Fn + Left/Right): same quintic code as auton turns ----
        if snap is None and snap_request != 0:
            if imu_ok and xd == 0 and xt == 0:
                snap = QuinticTurn(snap_request, SNAP_MAX_DPS, SNAP_MAX_ACCEL_DPS2)
                drive_sh.reset(0.0)
            snap_request = 0
        if snap is not None:
            if xd != 0 or xt != 0:
                # cancel instantly; hand the current turn rate to the shaper so there's no jolt
                turn_sh.reset(snap.rate)
                snap = None
                hold_target = None
            else:
                volts, done = snap.step()
                set_drive_volts(volts, -volts)
                if done:
                    hold_target = snap.target()
                    turn_sh.reset(0.0)
                    snap = None
                wait(LOOP_MS, MSEC)
                continue

        precision = precision_btn is not None and precision_btn.pressing()
        if precision:
            kd, kt, Pd, Pt = DRIVE_EXPO_PRECISION, TURN_EXPO_PRECISION, DRIVE_PRECISION, TURN_PRECISION
        else:
            kd, kt, Pd, Pt = DRIVE_EXPO, TURN_EXPO, 1.0, 1.0
        fd = expo(xd, kd)
        ft = expo(xt, kt)

        rot = imu_rot()
        Ld = drive_L.update(fd, drive_position_in(), precision, dt)
        Lt = turn_L.update(ft, rot, precision, dt)

        target_v = Pd * Ld * fd * DRIVER_DRIVE_MAX
        target_v *= tip_guard_drive_scale()   # v13 tip guard: lift high -> drive (not turn) at 50%; the shaper slows it down smoothly
        target_w = Pt * Lt * ft * DRIVER_TURN_MAX

        # spec 4: speed-dependent turn authority |w*| <= a_lat / |v|
        w_cap = (A_LAT / max(abs(drive_sh.v), 1e-3)) * 180.0 / math.pi
        target_w = clamp(target_w, -w_cap, w_cap)

        w = turn_sh.step(target_w, dt)

        # spec 4: turn priority at saturation -> take it out of forward speed, never the turn
        fwd_room = max(0.0, V_FREE - abs(dps_to_side(w)))
        target_v = clamp(target_v, -fwd_room, fwd_room)
        if abs(drive_sh.v) > fwd_room:
            drive_sh.v = sgn(drive_sh.v) * fwd_room
        v = drive_sh.step(target_v, dt)

        # heading hold: turn stick centered and driving -> lock IMU heading
        w_cmd = w
        if HEADING_HOLD and imu_ok and xt == 0 and (xd != 0 or abs(v) > HEADING_HOLD_MIN_SPEED):
            if hold_target is None:
                if abs(w) < HEADING_CAPTURE_DPS:
                    hold_target = rot
            else:
                w_cmd += clamp(HEADING_HOLD_KP * wrap180(hold_target - rot), -HEADING_HOLD_MAX_DPS, HEADING_HOLD_MAX_DPS)
        else:
            hold_target = None

        side_w = dps_to_side(w_cmd)
        side_wa = dps_to_side(turn_sh.a)
        left = side_ff_volts(v + side_w, drive_sh.a + side_wa)
        right = side_ff_volts(v - side_w, drive_sh.a - side_wa)
        set_drive_volts(left, right)
        wait(LOOP_MS, MSEC)

# ---------- v13 tip guard ----------
tip_guard_on = False

def tip_guard_drive_scale():
    # 1.0 normally; TIP_GUARD_DRIVE_SCALE (0.5) while the lift is high. On above TIP_GUARD_LIFT_DEG, off below TIP_GUARD_RELEASE_DEG.
    global tip_guard_on
    lift = LiftL1.position(DEGREES)
    if lift > TIP_GUARD_LIFT_DEG:
        tip_guard_on = True
    elif lift < TIP_GUARD_RELEASE_DEG:
        tip_guard_on = False
    if tip_guard_on:
        return TIP_GUARD_DRIVE_SCALE
    return 1.0

# ---------- quick tests (CONFIG: AUTON_TEST) ----------
def run_auton_test():
    brain.screen.clear_screen()
    brain.screen.set_font(FontType.MONO20)
    if AUTON_TEST == "DRIVE24":
        x0 = drive_position_in()
        h0 = imu_rot()
        auton_drive(24)
        wait(300, MSEC)
        moved = drive_position_in() - x0
        brain.screen.set_cursor(1, 1)
        brain.screen.print("Encoders: " + str(round(moved, 2)) + " in")
        brain.screen.set_cursor(2, 1)
        brain.screen.print("Heading drift: " + str(round(imu_rot() - h0, 1)))
        brain.screen.set_cursor(3, 1)
        brain.screen.print("Tape it: should be 24 in")
        print("DRIVE24 encoders " + str(round(moved, 2)) + " in, heading drift " + str(round(imu_rot() - h0, 1)))
    elif AUTON_TEST == "TURN90":
        h0 = imu_rot()
        auton_turn(90)
        wait(300, MSEC)
        brain.screen.set_cursor(1, 1)
        brain.screen.print("IMU turned: " + str(round(imu_rot() - h0, 1)) + " deg")
        print("TURN90 IMU turned " + str(round(imu_rot() - h0, 1)))
    elif AUTON_TEST == "TUNE":
        # v13 PID tuning run (~5 s): drive 24, turn 90, turn -90, drive -24.
        # After each step: e = distance error (inches, + = stopped short), h = heading error (deg, + = needs to turn more right).
        brain.screen.set_cursor(1, 1)
        brain.screen.print("TUNE  e=in  h=deg")
        controller_1.screen.clear_screen()
        results = []
        steps = [("D", 24), ("T", 90), ("T", -90), ("D", -24)]
        row = 4
        for kind, amount in steps:
            x0 = drive_position_in()
            if kind == "D":
                auton_drive(amount)
            else:
                auton_turn(amount)
            wait(300, MSEC)
            h = wrap180(auton_heading_target - imu_rot())
            if kind == "D":
                e = amount - (drive_position_in() - x0)
                if amount < 0:
                    e = -e        # backward: + still means stopped short
                line = kind + str(amount) + " e" + str(round(e, 2)) + " h" + str(round(h, 1))
            else:
                line = kind + str(amount) + " h" + str(round(h, 1))
            results.append(line)
            brain.screen.set_cursor(row, 1)
            brain.screen.print(line)
            row += 1
            print("TUNE " + line)
        controller_1.screen.set_cursor(1, 1)
        controller_1.screen.print(results[0])
        controller_1.screen.set_cursor(2, 1)
        controller_1.screen.print(results[1] + " " + results[2])
        controller_1.screen.set_cursor(3, 1)
        controller_1.screen.print(results[3])
# ==================================================================================================================

def when_started1():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    MaxSpeed = 0.5
    LiftR1.set_stopping(HOLD)
    LiftR2.set_stopping(HOLD)
    LiftL1.set_stopping(HOLD)
    LiftL2.set_stopping(HOLD)
    LiftR1.set_max_torque(100, PERCENT)
    LiftR2.set_max_torque(100, PERCENT)
    LiftL1.set_max_torque(100, PERCENT)
    LiftL2.set_max_torque(100, PERCENT)
    RearSpinner.set_velocity(40, PERCENT)  # was 100
    RearSpinner.set_max_torque(100, PERCENT)
    RearSpinner.set_stopping(HOLD)
    for motor in [L1, L2, L3, R1, R2, R3]:
        motor.set_max_torque(100, PERCENT)  # drivetrain: full torque allowed
    calibrate_imu()   # v12: shows "IMU calibrating" and waits; driver/auton won't move until it's done

def ondriver_drivercontrol_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    MaxSpeed = DRIVER_DRIVE_SPEED  # reset driver speed (auton sets MaxSpeed = 0.15)
    if USE_NEW_DRIVE:
        new_driver_loop()   # v12 pipeline (CONFIG: USE_NEW_DRIVE = False goes back to the v11 loop below)
        return
    while True:
        guard = tip_guard_drive_scale()   # v13 tip guard (drive only, not turn)
        SpeedLeft = (controller_1.axis3.position() * MaxSpeed * guard + controller_1.axis1.position() * DRIVER_TURN_SPEED) / 8.3  # fixed: now matches SpeedRight
        SpeedRight = (controller_1.axis3.position() * MaxSpeed * guard - controller_1.axis1.position() * DRIVER_TURN_SPEED) / 8.3
        L1.spin(FORWARD, SpeedLeft, VOLT)
        L2.spin(FORWARD, SpeedLeft, VOLT)
        L3.spin(FORWARD, SpeedLeft, VOLT)
        R1.spin(FORWARD, SpeedRight, VOLT)
        R2.spin(FORWARD, SpeedRight, VOLT)
        R3.spin(FORWARD, SpeedRight, VOLT)
        wait(5, MSEC)

def onauton_autonomous_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    MaxSpeed = 0.15
    wait_for_imu()               # v12: never move before the IMU is calibrated
    auton_setup()
    if AUTON_TEST != "NONE":     # v12: CONFIG AUTON_TEST = "DRIVE24" / "TURN90" runs just that test
        run_auton_test()
        auton_finish()
        return
    # v12 RESCALE: v11 distances went through the old formula (2.75 in wheel, no gearing), so the robot really
    # traveled  old x (0.75 x 3.25 / 2.75) = old x 0.886.  Now inches are real inches, so these keep the SAME path:
    #   22 -> 19.5,  51.3 -> 45.5,  7.3 -> 6.5,  36.7 -> 32.5
    # Turns are now true robot degrees on the IMU (TURN_DEG_PER_ROBOT_DEG note in CONFIG):
    #   step 4: old 1.1 in = 1.1/(pi x 2.75) x 360 = 45.8 motor deg -> 45.8 / 4.73 = 9.7 robot deg
    #   step 9: old 230 x 3.7 = 851 motor deg -> 851 / 4.73 = 180 robot deg (a true turn-around)
    # v13 NOTE: DRIVE_DISTANCE_SCALE (1.116) now makes these real inches. Before v13 the robot went ~10% short of each number
    # (DRIVE24 test: 21.5 of 24), so this path now travels ~11.6% farther than v12 did. Re-check the path at practice.
    claw_set(True)               # 1. close the claw right away
    wait(800, MSEC)
    Lift_Up_inches(6.5)          # 2. lift up
    Forward_inches(19.5)         # 3. forward (v11: 22)
    wait(800, MSEC)
    Turn_side_robot_degrees(9.7) # 4. small turn toward AUTON_SIDE (v11: Turn_side_inches(1.1))
    wait(800, MSEC)
    Forward_inches(45.5)         # 5. forward (v11: 51.3)
    Lift_Down_inches(8)          # 6. lift down
    wait(800, MSEC)
    claw_set(False)              # 7. open the claw (let go)
    wait(500, MSEC)
    Backward_inches(6.5)         # 8. back up (v11: 7.3)
    Turn_side_robot_degrees(180) # 9. turn around (v11: 230 in old units)
    Forward_inches(32.5)         # 10. forward (v11: 36.7)
    auton_finish()

def controller_1buttonX_pressed_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    LiftL1.set_stopping(COAST)
    LiftL2.set_stopping(COAST)
    LiftR1.set_stopping(COAST)
    LiftR2.set_stopping(COAST)
    wait(1, SECONDS)
    LiftL1.set_stopping(HOLD)
    LiftL2.set_stopping(HOLD)
    LiftR1.set_stopping(HOLD)
    LiftR2.set_stopping(HOLD)

def controller_1buttonDown_pressed_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    if fn_arrow("Down"):   # v12: Fn + Down = macro_down(); plain Down still toggles rotate below
        return
    if pneumaticRotate:
        PuematicRotate.set(True)
        pneumaticRotate = False
    else:
        PuematicRotate.set(False)
        pneumaticRotate = True

def controller_1buttonB_pressed_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    if pneumaticClaw:
        PneumaticClaw.set(True)
        pneumaticClaw = False
    else:
        PneumaticClaw.set(False)
        pneumaticClaw = True

def controller_1buttonY_pressed_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    if puematicTilt:
        PneumaticTilt.set(True)
        puematicTilt = False
    else:
        PneumaticTilt.set(False)
        puematicTilt = True

def controller_1buttonR1_pressed_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    RearSpinner.spin(REVERSE)

def controller_1buttonR1_released_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    RearSpinner.stop()

def controller_1buttonR2_pressed_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    RearSpinner.spin(FORWARD)

def controller_1buttonR2_released_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    RearSpinner.stop()

# ---------- v13 lift ramp: speed ramps up on press and down on release (no instant 50% / slam stop) ----------
lift_cmd_pct = 0.0     # lift speed the driver ramp is commanding right now, % (+ = up, - = down)
lift_ramp_id = 0       # bumped on every L1/L2 press/release so an older ramp loop stops when a newer one starts

def lift_ramp_toward(current, target, dt):
    # move current toward target by at most LIFT_DRIVER_SPEED per LIFT_RAMP_SEC
    step = LIFT_DRIVER_SPEED * dt / LIFT_RAMP_SEC
    if current < target:
        return min(target, current + step)
    return max(target, current - step)

def lift_spin_pct(pct):
    # + = up (FORWARD, same as v11 L1), - = down (REVERSE, same as v11 L2)
    direction = FORWARD
    if pct < 0:
        direction = REVERSE
    for motor in [LiftR1, LiftL1, LiftL2, LiftR2]:
        motor.set_velocity(abs(pct), PERCENT)
        motor.spin(direction)

def lift_stop_hold():
    LiftL1.stop()
    LiftR1.stop()
    LiftL2.stop()
    LiftR2.stop()

def lift_driver_hold(button, target_pct):
    # runs while L1/L2 is held: ramp toward +/-LIFT_DRIVER_SPEED, stop at the 0 / 900 limits like v11
    global lift_cmd_pct, lift_ramp_id
    lift_ramp_id += 1
    my_id = lift_ramp_id
    last_ms = brain.timer.time(MSEC)
    while button.pressing() and my_id == lift_ramp_id:
        now = brain.timer.time(MSEC)
        dt = (now - last_ms) / 1000.0
        last_ms = now
        pos = LiftL1.position(DEGREES)
        if (target_pct > 0 and pos <= 900) or (target_pct < 0 and pos > 0):
            printdegrees()
            lift_cmd_pct = lift_ramp_toward(lift_cmd_pct, target_pct, dt)
            lift_spin_pct(lift_cmd_pct)
        else:
            # at the 900 top / 0 bottom limit, actually stop the lift
            lift_cmd_pct = 0.0
            lift_stop_hold()
        wait(5, MSEC)

def lift_driver_release():
    # L1/L2 let go: ramp the speed down to 0 over LIFT_RAMP_SEC, THEN stop on HOLD (no full-torque slam)
    global lift_cmd_pct, lift_ramp_id
    lift_ramp_id += 1
    my_id = lift_ramp_id
    last_ms = brain.timer.time(MSEC)
    while lift_cmd_pct != 0 and my_id == lift_ramp_id:
        pos = LiftL1.position(DEGREES)
        if (lift_cmd_pct > 0 and pos > 900) or (lift_cmd_pct < 0 and pos <= 0):
            break        # never coast past a limit while ramping down
        now = brain.timer.time(MSEC)
        dt = (now - last_ms) / 1000.0
        last_ms = now
        lift_cmd_pct = lift_ramp_toward(lift_cmd_pct, 0.0, dt)
        if lift_cmd_pct == 0:
            break
        lift_spin_pct(lift_cmd_pct)
        wait(5, MSEC)
    if my_id == lift_ramp_id:   # a new L1/L2 press didn't take over
        lift_cmd_pct = 0.0
        lift_stop_hold()

def controller_1buttonL1_pressed_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    lift_driver_hold(controller_1.buttonL1, LIFT_DRIVER_SPEED)    # v13: ramped (v11: instant 50% up)

def controller_1buttonL2_pressed_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    lift_driver_hold(controller_1.buttonL2, -LIFT_DRIVER_SPEED)   # v13: ramped (v11: instant 50% down)

def controller_1buttonL1_released_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    lift_driver_release()   # v13: ramp down, then HOLD

def controller_1buttonL2_released_callback_0():
    global pneumaticClaw, pneumaticRotate, puematicTilt, SpeedLeft, SpeedRight, MaxSpeed, screen_precision, console_precision, controller_1_precision
    lift_driver_release()   # v13: ramp down, then HOLD

# create a function for handling the starting and stopping of all autonomous tasks
def autonomous():
    # Start the autonomous control tasks
    auton_task_0 = Thread( onauton_autonomous_0 )
    # wait for the driver control period to end
    while( comp.is_autonomous() and comp.is_enabled() ):
        # wait 10 milliseconds before checking again
        wait( 10, MSEC )
    # Stop the autonomous control tasks
    auton_task_0.stop()

def user_control():
    # Start the driver control tasks
    driver_control_task_0 = Thread( ondriver_drivercontrol_0 )

    # wait for the driver control period to end
    while( comp.is_driver_control() and comp.is_enabled() ):
        # wait 10 milliseconds before checking again
        wait( 10, MSEC )
    # Stop the driver control tasks
    driver_control_task_0.stop()


# create competition instance (registers the competition functions)
comp = Competition(user_control, autonomous)

# actions to do when the program starts
# system event handlers
controller_1.buttonX.pressed(controller_1buttonX_pressed_callback_0)
controller_1.buttonDown.pressed(controller_1buttonDown_pressed_callback_0)
controller_1.buttonB.pressed(controller_1buttonB_pressed_callback_0)
controller_1.buttonY.pressed(controller_1buttonY_pressed_callback_0)
controller_1.buttonR1.pressed(controller_1buttonR1_pressed_callback_0)
controller_1.buttonR1.released(controller_1buttonR1_released_callback_0)
if KEEP_R2_SPINNER:   # v12: R2 is precision/Fn now; old spinner binding only if you turn it back on
    controller_1.buttonR2.pressed(controller_1buttonR2_pressed_callback_0)
    controller_1.buttonR2.released(controller_1buttonR2_released_callback_0)
# v12: arrows do Fn jobs only while FN_BUTTON is held (Down without Fn = rotate, above)
controller_1.buttonUp.pressed(controller_1buttonUp_pressed_callback_0)
controller_1.buttonLeft.pressed(controller_1buttonLeft_pressed_callback_0)
controller_1.buttonRight.pressed(controller_1buttonRight_pressed_callback_0)
controller_1.buttonL1.pressed(controller_1buttonL1_pressed_callback_0)
controller_1.buttonL2.pressed(controller_1buttonL2_pressed_callback_0)
controller_1.buttonL1.released(controller_1buttonL1_released_callback_0)
controller_1.buttonL2.released(controller_1buttonL2_released_callback_0)
# add 15ms delay to make sure events are registered correctly.
wait(15, MSEC)

when_started1()
