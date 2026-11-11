#region VEXcode Generated Robot Configuration
from vex import *
import math

brain = Brain()
controller_1 = Controller(PRIMARY)
L1 = Motor(Ports.PORT10, GearSetting.RATIO_6_1, False)
L2 = Motor(Ports.PORT9, GearSetting.RATIO_6_1, False)
R1 = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
R2 = Motor(Ports.PORT2, GearSetting.RATIO_6_1, True)
LiftL1 = Motor(Ports.PORT7, GearSetting.RATIO_18_1, False)
LiftL2 = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)
LiftR1 = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)
LiftR2 = Motor(Ports.PORT5, GearSetting.RATIO_18_1, True)
Claw = DigitalOut(brain.three_wire_port.a)
RearSpinner = Motor(Ports.PORT21, GearSetting.RATIO_18_1, False)
print("\033[2J")

imu = Inertial(Ports.PORT15)

#--------------------------------------------------------------
# 1. CONSTANTS
#--------------------------------------------------------------
DRIVE_MOTORS = [L1, L2, R1, R2]
LIFT_MOTORS = [LiftL1, LiftL2, LiftR1, LiftR2]

DRIVE_TORQUE = 100
TURN_RATIO = 0.6

TURN_MAX = 60.0
L1_MAX_VEL = 100.0
L2_MAX_VEL = 100.0
R1_MAX_VEL = 80.0
R2_MAX_VEL = 80.0
DRIVE_SIGN = -1.0

HEADING_KP = 1.0
HEADING_MAX_CORR = 20.0
HEADING_TOL_DEG = 1.0
DEADBAND = 0.05
KNEE_STICK = 0.85
KNEE_VEL = 50.0

AUTON_COEF = 0.65
AUTON_LIFT_INCHES = 1.0
AUTON_CLAW_SETTLE_MS = 500

WHEEL_DIAMETER = 3.25
DRIVE_GEAR_RATIO = 0.75
LIFT_DEG_PER_INCH = 64
LIFT_VEL = 50

SNAP_TOL_DEG = 3.0
IMU_TURN_SIGN = -1.0
TURN_TIMEOUT_MS = 1000
SMOOTH_TAU = 0

DRIVE_MAX_VEL = 100.0
DRIVE_START_REG = 30.0
DRIVE_START_FN = 70.0
SPEED_ADJ_STEP = 10.0
SPEED_ADJ_MIN = 10.0
SPEED_ADJ_MAX = 100.0

DEFENSE_SPIN_VEL = 90.0
DEFENSE_SPIN_DIR = 1.0
DEFENSE_RETURN_VEL = 60.0

claw_closed = False
imu_ready = False
snap_target = None
heading_target = None
reg_adj_pct = DRIVE_START_REG
fn_adj_pct = DRIVE_START_FN
defense_on = False
defense_return = False
defense_heading = None

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
    L1.spin(FORWARD, clamp(DRIVE_SIGN * left_pct, -L1_MAX_VEL, L1_MAX_VEL), PERCENT)
    L2.spin(FORWARD, clamp(DRIVE_SIGN * left_pct, -L2_MAX_VEL, L2_MAX_VEL), PERCENT)
    R1.spin(FORWARD, clamp(DRIVE_SIGN * right_pct, -R1_MAX_VEL, R1_MAX_VEL), PERCENT)
    R2.spin(FORWARD, clamp(DRIVE_SIGN * right_pct, -R2_MAX_VEL, R2_MAX_VEL), PERCENT)

def stop_drive():
    for m in DRIVE_MOTORS:
        m.stop(COAST)

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
    loops = 0
    max_loops = TURN_TIMEOUT_MS // 10
    while True:
        err = wrap180(target - imu.rotation(DEGREES))
        if abs(err) < SNAP_TOL_DEG:
            break
        if loops >= max_loops:
            break
        loops += 1
        v = vel_pct if abs(err) > 15.0 else 25.0
        cmd = IMU_TURN_SIGN * math.copysign(v, err)
        set_drive(cmd, -cmd)
        wait(10, MSEC)
    for m in DRIVE_MOTORS:
        m.stop(BRAKE)

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
        v = KNEE_VEL + ((a - KNEE_STICK) / (1.0 - KNEE_STICK)) * (DRIVE_MAX_VEL - KNEE_VEL)
    return math.copysign(v, s)

def turn_map(s, max_vel):
    a = abs(s)
    if a < DEADBAND:
        return 0.0
    return math.copysign(a * max_vel, s)

def driver_loop():
    global snap_target, heading_target, defense_on, defense_return, defense_heading
    wait_for_imu()
    left_s = 0.0
    right_s = 0.0
    lift_s = 0.0
    dt = 0.02
    k = min(1.0, dt / SMOOTH_TAU) if SMOOTH_TAU > 0 else 1.0
    while True:
        fn = controller_1.buttonR2.pressing()
        if defense_return:
            defense_return = False
            imu_turn(wrap180(defense_heading - imu.rotation(DEGREES)), DEFENSE_RETURN_VEL)
            heading_target = None
            left_s = 0.0
            right_s = 0.0
            continue
        if defense_on:
            snap_target = None
            heading_target = None
            left_s = 0.0
            right_s = 0.0
            set_drive(DEFENSE_SPIN_DIR * DEFENSE_SPIN_VEL, -DEFENSE_SPIN_DIR * DEFENSE_SPIN_VEL)
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
            continue
        if snap_target is not None:
            imu_turn(snap_target, TURN_MAX)
            snap_target = None
            heading_target = None
            left_s = 0.0
            right_s = 0.0
            continue
        active_pct = fn_adj_pct if fn else reg_adj_pct
        turn_max = TURN_RATIO * active_pct
        dv = drive_map(controller_1.axis3.position() / 100.0) * (active_pct / 100.0)
        tv = turn_map(controller_1.axis1.position() / 100.0, turn_max)
        if tv == 0.0 and dv != 0.0:
            if heading_target is None:
                heading_target = imu.rotation(DEGREES)
            herr = wrap180(heading_target - imu.rotation(DEGREES))
            if abs(herr) > HEADING_TOL_DEG:
                tv += clamp(herr * HEADING_KP, -HEADING_MAX_CORR, HEADING_MAX_CORR)
        else:
            heading_target = None
        tv = clamp(tv, -turn_max, turn_max)
        left_s += ((dv + tv) - left_s) * k
        right_s += ((dv - tv) - right_s) * k
        if abs(left_s) < 0.5 and abs(right_s) < 0.5:
            for m in DRIVE_MOTORS:
                m.stop(COAST)
        else:
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

def on_up():
    global reg_adj_pct, fn_adj_pct
    if controller_1.buttonR2.pressing():
        fn_adj_pct = clamp(fn_adj_pct + SPEED_ADJ_STEP, SPEED_ADJ_MIN, SPEED_ADJ_MAX)
    else:
        reg_adj_pct = clamp(reg_adj_pct + SPEED_ADJ_STEP, SPEED_ADJ_MIN, SPEED_ADJ_MAX)

def on_down():
    global reg_adj_pct, fn_adj_pct
    if controller_1.buttonR2.pressing():
        fn_adj_pct = clamp(fn_adj_pct - SPEED_ADJ_STEP, SPEED_ADJ_MIN, SPEED_ADJ_MAX)
    else:
        reg_adj_pct = clamp(reg_adj_pct - SPEED_ADJ_STEP, SPEED_ADJ_MIN, SPEED_ADJ_MAX)

def on_y():
    global defense_on, defense_return, defense_heading
    if defense_return:
        return
    if defense_on:
        defense_on = False
        defense_return = True
    else:
        defense_heading = imu.rotation(DEGREES)
        defense_on = True

#--------------------------------------------------------------
# 4. MECHANISMS
#--------------------------------------------------------------
def claw_set(closed):
    global claw_closed
    claw_closed = closed
    Claw.set(claw_closed)

def claw_close():
    claw_set(True)

def claw_toggle():
    claw_set(not claw_closed)

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
    claw_close()
    wait(AUTON_CLAW_SETTLE_MS, MSEC)
    lift_inches(AUTON_LIFT_INCHES)
    stop_drive()

#--------------------------------------------------------------
# 6. WHEN STARTED
#--------------------------------------------------------------
def startup():
    claw_close()
    for m in LIFT_MOTORS:
        m.set_stopping(HOLD)
        m.set_max_torque(100, PERCENT)
    for m in DRIVE_MOTORS:
        m.set_stopping(COAST)
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
controller_1.buttonY.pressed(on_y)
controller_1.buttonUp.pressed(on_up)
controller_1.buttonDown.pressed(on_down)
controller_1.buttonLeft.pressed(on_left)
controller_1.buttonRight.pressed(on_right)

startup()
