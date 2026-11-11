#region VEXcode Generated Robot Configuration
from vex import *
import math

brain = Brain()
controller_1 = Controller(PRIMARY)
L2 = Motor(Ports.PORT9, GearSetting.RATIO_6_1, True)
L3 = Motor(Ports.PORT10, GearSetting.RATIO_6_1, True)
R1 = Motor(Ports.PORT1, GearSetting.RATIO_6_1, False)
R2 = Motor(Ports.PORT2, GearSetting.RATIO_6_1, False)
LiftL1 = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)
LiftL2 = Motor(Ports.PORT7, GearSetting.RATIO_18_1, False)
LiftR1 = Motor(Ports.PORT5, GearSetting.RATIO_18_1, True)
LiftR2 = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)
PneumaticClaw = DigitalOut(brain.three_wire_port.g)
PneumaticTilt = DigitalOut(brain.three_wire_port.f)
PneumaticRotate = DigitalOut(brain.three_wire_port.h)
RearSpinner = Motor(Ports.PORT21, GearSetting.RATIO_18_1, False)
print("\033[2J")

imu = Inertial(Ports.PORT15)

#--------------------------------------------------------------
# 1. CONSTANTS
#--------------------------------------------------------------
DRIVE_MOTORS = [L2, L3, R1, R2]
LIFT_MOTORS = [LiftL1, LiftL2, LiftR1, LiftR2]

DRIVE_TORQUE = 100
FN_TORQUE = 50
FN_VEL_SCALE = 0.35

TURN_MAX = 60.0
DEADBAND = 0.05
KNEE_STICK = 0.85
KNEE_VEL = 50.0

AUTON_COEF = 0.65

WHEEL_DIAMETER = 3.25
DRIVE_GEAR_RATIO = 0.75
LIFT_DEG_PER_INCH = 64
LIFT_VEL = 50

SNAP_TOL_DEG = 3.0
SMOOTH_TAU = 0.08

claw_closed = False
tilt_out = False
rotate_out = False
imu_ready = False
snap_target = None

#--------------------------------------------------------------
# 2. HELPERS
#--------------------------------------------------------------
def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def wrap180(a):
    while a > 180.0:
        a -= 360.0
    while a < -180.0:
        a += 360.0
    return a

def set_drive(left_pct, right_pct):
    left_pct = clamp(left_pct, -100.0, 100.0)
    right_pct = clamp(right_pct, -100.0, 100.0)
    L2.spin(FORWARD, left_pct, PERCENT)
    L3.spin(FORWARD, left_pct, PERCENT)
    R1.spin(FORWARD, right_pct, PERCENT)
    R2.spin(FORWARD, right_pct, PERCENT)

def stop_drive():
    for m in DRIVE_MOTORS:
        m.stop(BRAKE)

def calibrate_imu():
    global imu_ready
    imu.calibrate()
    while imu.is_calibrating():
        wait(10, MSEC)
    imu_ready = True

def wait_for_imu():
    while not imu_ready:
        wait(10, MSEC)

def imu_turn(deg, vel_pct):
    target = imu.rotation(DEGREES) + deg
    while True:
        err = wrap180(target - imu.rotation(DEGREES))
        if abs(err) < SNAP_TOL_DEG:
            break
        v = vel_pct if abs(err) > 15.0 else 25.0
        cmd = math.copysign(v, err)
        set_drive(cmd, -cmd)
        wait(10, MSEC)
    stop_drive()

#--------------------------------------------------------------
# 3. DRIVER
#--------------------------------------------------------------
def drive_map(s):
    a = abs(s)
    if a < DEADBAND:
        return 0.0
    if a < KNEE_STICK:
        v = (a / KNEE_STICK) * KNEE_VEL
    else:
        v = KNEE_VEL + ((a - KNEE_STICK) / (1.0 - KNEE_STICK)) * (100.0 - KNEE_VEL)
    return math.copysign(v, s)

def turn_map(s):
    a = abs(s)
    if a < DEADBAND:
        return 0.0
    return math.copysign(a * TURN_MAX, s)

def driver_loop():
    global snap_target
    wait_for_imu()
    fn_was = False
    left_s = 0.0
    right_s = 0.0
    lift_s = 0.0
    dt = 0.02
    k = min(1.0, dt / SMOOTH_TAU) if SMOOTH_TAU > 0 else 1.0
    while True:
        fn = controller_1.buttonR2.pressing()
        if fn != fn_was:
            for m in DRIVE_MOTORS:
                m.set_max_torque(FN_TORQUE if fn else DRIVE_TORQUE, PERCENT)
            fn_was = fn
        if snap_target is not None:
            imu_turn(snap_target, TURN_MAX)
            snap_target = None
            left_s = 0.0
            right_s = 0.0
            continue
        dv = drive_map(controller_1.axis3.position() / 100.0)
        tv = turn_map(controller_1.axis1.position() / 100.0)
        if fn:
            dv *= FN_VEL_SCALE
            tv *= FN_VEL_SCALE
        left_s += ((dv + tv) - left_s) * k
        right_s += ((dv - tv) - right_s) * k
        set_drive(left_s, right_s)
        if controller_1.buttonL1.pressing():
            lift_t = LIFT_VEL
        elif controller_1.buttonL2.pressing():
            lift_t = -LIFT_VEL
        else:
            lift_t = 0.0
        lift_s += (lift_t - lift_s) * k
        if lift_t == 0.0 and abs(lift_s) < 1.0:
            for m in LIFT_MOTORS:
                m.stop(HOLD)
        else:
            for m in LIFT_MOTORS:
                m.spin(FORWARD, lift_s, PERCENT)
        if controller_1.buttonR1.pressing():
            RearSpinner.spin(REVERSE, 100, PERCENT)
        else:
            RearSpinner.stop()
        wait(20, MSEC)

def on_left():
    global snap_target
    if controller_1.buttonR2.pressing():
        snap_target = -90.0

def on_right():
    global snap_target
    if controller_1.buttonR2.pressing():
        snap_target = 90.0

#--------------------------------------------------------------
# 4. MECHANISMS
#--------------------------------------------------------------
def claw_toggle():
    global claw_closed
    claw_closed = not claw_closed
    PneumaticClaw.set(claw_closed)

def tilt_toggle():
    global tilt_out
    tilt_out = not tilt_out
    PneumaticTilt.set(tilt_out)

def rotate_toggle():
    global rotate_out
    rotate_out = not rotate_out
    PneumaticRotate.set(rotate_out)

def lift_inches(inches):
    deg = inches * LIFT_DEG_PER_INCH
    for m in LIFT_MOTORS:
        m.spin_to_position(m.position(DEGREES) + deg, DEGREES, LIFT_VEL, PERCENT, False)
    for m in LIFT_MOTORS:
        while m.is_spinning():
            wait(10, MSEC)
    for m in LIFT_MOTORS:
        m.stop(HOLD)

#--------------------------------------------------------------
# 5. AUTON
#--------------------------------------------------------------
def auton_drive_inches(inches):
    vel = AUTON_COEF * 100.0
    if inches < 0:
        vel = -vel
    target_deg = abs(inches) / (math.pi * WHEEL_DIAMETER * DRIVE_GEAR_RATIO) * 360.0
    for m in DRIVE_MOTORS:
        m.set_position(0, DEGREES)
    set_drive(vel, vel)
    while True:
        avg = sum(m.position(DEGREES) for m in DRIVE_MOTORS) / 4.0
        if abs(avg) >= target_deg:
            break
        wait(10, MSEC)
    stop_drive()

def auton_turn_deg(deg):
    imu_turn(deg, AUTON_COEF * TURN_MAX)

def run_autonomous():
    wait_for_imu()
    claw_toggle()
    wait(800, MSEC)
    lift_inches(6.5)
    auton_drive_inches(38.0)
    wait(800, MSEC)
    auton_turn_deg(9.7)
    wait(800, MSEC)
    auton_drive_inches(45.5)
    lift_inches(-8.0)
    wait(800, MSEC)
    claw_toggle()
    wait(500, MSEC)
    auton_drive_inches(-6.5)
    auton_turn_deg(180.0)
    auton_drive_inches(32.5)
    stop_drive()

#--------------------------------------------------------------
# 6. WHEN STARTED
#--------------------------------------------------------------
def startup():
    for m in LIFT_MOTORS:
        m.set_stopping(HOLD)
        m.set_max_torque(100, PERCENT)
    for m in DRIVE_MOTORS:
        m.set_max_torque(DRIVE_TORQUE, PERCENT)
    RearSpinner.set_max_torque(100, PERCENT)
    calibrate_imu()

def autonomous():
    auton_task = Thread(run_autonomous)
    while comp.is_autonomous() and comp.is_enabled():
        wait(10, MSEC)
    auton_task.stop()

def user_control():
    driver_task = Thread(driver_loop)
    while comp.is_driver_control() and comp.is_enabled():
        wait(10, MSEC)
    driver_task.stop()

comp = Competition(user_control, autonomous)

controller_1.buttonB.pressed(claw_toggle)
controller_1.buttonY.pressed(tilt_toggle)
controller_1.buttonDown.pressed(rotate_toggle)
controller_1.buttonLeft.pressed(on_left)
controller_1.buttonRight.pressed(on_right)

startup()
