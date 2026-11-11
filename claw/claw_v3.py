#region VEXcode Generated Robot Configuration
from vex import *
import urandom
import math

# Brain should be defined by default
brain=Brain()

# Robot configuration code
controller_1 = Controller(PRIMARY)
L2 = Motor(Ports.PORT9, GearSetting.RATIO_6_1, True)
L3 = Motor(Ports.PORT10, GearSetting.RATIO_6_1, True)
R1 = Motor(Ports.PORT1, GearSetting.RATIO_6_1, False)
LiftL1 = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)
LiftR1 = Motor(Ports.PORT5, GearSetting.RATIO_18_1, True)
PneumaticClaw = DigitalOut(brain.three_wire_port.g)
RearSpinner = Motor(Ports.PORT21, GearSetting.RATIO_18_1, False)
PneumaticTilt = DigitalOut(brain.three_wire_port.f)
PneumaticRotate = DigitalOut(brain.three_wire_port.h)
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
imu = Inertial(Ports.PORT15)
#--------------------------------------------------------------
# 2. CONSTANTS → SELF-TUNED
#--------------------------------------------------------------

if True:
    SERIES = "fresh"
    VERSION = 3

    DRIVE_MOTORS = [L2, L3, R1, R2]
    LIFT_MOTORS = [LiftL1, LiftL2, LiftR1, LiftR2]

    # --- Master switch ---
    AUTON_TEST = "NONE"

    # --- Drive heading correction ---
    DRIVE_HEADING_KP = 0.15
    DRIVE_HEADING_MAX_V = 3.0
    DRIVE_DISTANCE_SCALE = 1.116

    # --- Turn ---
    TURN_KP = 0.25
    TURN_KI = 0.0
    TURN_KD = 0.02
    TURN_TOL_DEG = 1.0
    TURN_SETTLE_DPS = 5.0

    # --- Settle ---
    SETTLE_LOOPS = 5
    SETTLE_MARGIN_SEC = 0.5

    # --- Buttons ---
    PRECISION_BUTTON = "R2"
    FN_BUTTON = "R2"
    FN_SNAP_LEFT = "Left"
    FN_SNAP_RIGHT = "Right"

    AUTON_SIDE = "RIGHT"

    # --- Geometry ---
    WHEEL_DIAMETER = 3.25
    DRIVE_GEAR_RATIO = 0.75
    TRACK_WIDTH = 10.0
    MOTOR_FREE_RPM = 600
    ROBOT_WEIGHT_LB = 15.0
    CG_TIP_RATIO = 1.0

    # --- Derived - speeds ---
    V_FREE = MOTOR_FREE_RPM * DRIVE_GEAR_RATIO * math.pi * WHEEL_DIAMETER / 60.0
    TURN_FREE_DPS = (2.0 * V_FREE / TRACK_WIDTH) * 180.0 / math.pi

    G_IN_S2 = 386.09
    # --- Derived - forces and feedforward ---
    MU = 0.9
    KAPPA = 0.6
    KAPPA_BRAKE = 0.6
    A_MOTOR = (6 * 0.35 / DRIVE_GEAR_RATIO / (WHEEL_DIAMETER / 2 * 0.0254)) / (ROBOT_WEIGHT_LB * 0.4536) / 0.0254
    A_TRACTION = KAPPA * MU * G_IN_S2
    A_BRAKE = min(KAPPA_BRAKE * MU * G_IN_S2, G_IN_S2 * CG_TIP_RATIO)
    DRIVER_BRAKE_SCALE = 0.7
    A_LAT = KAPPA * MU * G_IN_S2

    KV = 12.0 / V_FREE
    KA = 12.0 / A_MOTOR
    KS = 0.5
    KS_RAMP_IN_S = 1.0
    TURN_FF_SCALE = 1.0

    # --- Driver feel ---
    DRIVE_DEADBAND = 0.06
    TURN_DEADBAND = 0.08
    DRIVE_EXPO = 0.55
    TURN_EXPO = 0.75
    DRIVE_EXPO_PRECISION = 0.35
    TURN_EXPO_PRECISION = 0.40

    DRIVE_L0 = 0.65
    TURN_L0 = 0.55
    DRIVE_UNLOCK_IN = 18.0
    TURN_UNLOCK_DEG = 25.0
    STROKE_START = 0.85
    STROKE_END = 0.60
    UNLOCK_FALL_TAU = 0.10

    DRIVE_PRECISION = 0.30
    TURN_PRECISION = 0.35

    WN_UP = 17.5
    WN_DOWN = 1.75 * WN_UP

    HEADING_HOLD = True
    HEADING_HOLD_KP = 4.0
    HEADING_HOLD_MAX_DPS = 60.0
    HEADING_CAPTURE_DPS = 10.0
    HEADING_HOLD_MIN_SPEED = 2.0

    # --- Snap turns ---
    SNAP_DEG = 90
    SNAP_MAX_DPS = 350.0
    SNAP_ACCEL_SCALE = 1.0
    TURN_TRACTION_ACCEL_DPS2 = A_TRACTION / (TRACK_WIDTH / 2) * 180 / math.pi
    SNAP_MAX_ACCEL_DPS2 = TURN_TRACTION_ACCEL_DPS2 * SNAP_ACCEL_SCALE

    # --- Auton motion ---
    AUTON_DRIVE_SPEED = 25
    AUTON_V_MAX = AUTON_DRIVE_SPEED / 100.0 * V_FREE
    AUTON_ACCEL = A_TRACTION
    AUTON_JERK_TIME = 0.10
    AUTON_TURN_MAX_DPS = 350.0
    AUTON_TURN_ACCEL_DPS2 = TURN_TRACTION_ACCEL_DPS2

    # --- Lift and tip guard ---
    LIFT_DEG_PER_INCH = 64
    LIFT_MAX_DEGREES = 900
    LIFT_DOWN_SPEED = 50
    LIFT_DRIVER_SPEED = 50
    LIFT_BRAKE_SCALE = 0.7
    LIFT_RAMP_SEC = 0.2

    TIP_GUARD_LIFT_DEG = 425
    TIP_GUARD_DRIVE_SCALE = 0.50
    TIP_GUARD_RELEASE_DEG = 400

    # --- Misc ---
    CLAW_CLOSED_OUTPUT = False
    LIFT_MOVE_TIMEOUT_SEC = 2
    LOOP_MS = 10

    # --- State - do not tune ---
    pneumaticClaw = True
    pneumaticRotate = False
    pneumaticTilt = False

    imu_ready = False
    imu_ok = False
    auton_heading_target = 0.0
    auton_start_ms = 0

    snap_request = 0

    macro_running = False
    macro_abort = False
    fn_let_go = False


    tip_guard_on = False

    lift_cmd_pct = 0.0
    lift_ramp_id = 0


if True:  # MACHINERY
    # MACHINERY - NEVER TOUCH. Collapse this whole block.
    # ----------------------------------------------

    def sgn(x):
        if x > 0:
            return 1.0
        if x < 0:
            return -1.0
        return 0.0

    def clamp(x, lo, hi):
        return max(lo, min(hi, x))

    def wrap180(deg):
        while deg > 180:
            deg -= 360
        while deg < -180:
            deg += 360
        return deg

    def deadband(r, d):
        if abs(r) <= d:
            return 0.0
        return sgn(r) * (abs(r) - d) / (1.0 - d)

    def expo(x, k):
        ax = abs(x)
        return sgn(x) * ((1.0 - k) * ax + k * ax * ax * ax)

    def smoothstep(q):
        q = clamp(q, 0.0, 1.0)
        return 3.0 * q * q - 2.0 * q * q * q

    def quintic(tau):
        s = 10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5
        v = 30 * tau ** 2 - 60 * tau ** 3 + 30 * tau ** 4
        a = 60 * tau - 180 * tau ** 2 + 120 * tau ** 3
        return s, v, a

    def calibrate_imu():
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
            print("NO IMU on port 15!")
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
        if not imu_ok:
            return 0.0
        return imu.rotation(DEGREES)

    def motor_deg_to_inches(motor_degrees):
        return motor_degrees / 360.0 * DRIVE_GEAR_RATIO * math.pi * WHEEL_DIAMETER / DRIVE_DISTANCE_SCALE

    def drive_position_in():
        left = (L2.position(DEGREES) + L3.position(DEGREES)) / 2.0
        right = (R1.position(DEGREES) + R2.position(DEGREES)) / 2.0
        return motor_deg_to_inches((left + right) / 2.0)

    def drive_speed_in_s():
        rpm = (L2.velocity(RPM) + L3.velocity(RPM) + R1.velocity(RPM) + R2.velocity(RPM)) / 4.0
        return rpm / 60.0 * DRIVE_GEAR_RATIO * math.pi * WHEEL_DIAMETER / DRIVE_DISTANCE_SCALE

    def set_drive_volts(left_v, right_v):
        left_v = clamp(left_v, -12.0, 12.0)
        right_v = clamp(right_v, -12.0, 12.0)
        L2.spin(FORWARD, left_v, VOLT)
        L3.spin(FORWARD, left_v, VOLT)
        R1.spin(FORWARD, right_v, VOLT)
        R2.spin(FORWARD, right_v, VOLT)

    def stop_drive(mode):
        for motor in DRIVE_MOTORS:
            motor.stop(mode)

    def ks_term(speed_in_s):
        return KS * clamp(speed_in_s / KS_RAMP_IN_S, -1.0, 1.0)

    def side_ff_volts(speed_in_s, accel_in_s2):
        return KV * speed_in_s + KA * accel_in_s2 + ks_term(speed_in_s)

    def dps_to_side(dps):
        return dps * math.pi / 180.0 * TRACK_WIDTH / 2.0

    def side_to_dps(in_s):
        return in_s / (TRACK_WIDTH / 2.0) * 180.0 / math.pi

    class Ceiling:
        def __init__(self, L0, s_u):
            self.L0 = L0
            self.s_u = s_u
            self.L = L0
            self.active = False
            self.start = 0.0

        def update(self, f, progress, precision, dt):
            if precision:
                self.active = False
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

    class Shaper:
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
            if (v - target) * (v_new - target) < 0:
                v_new = target
                a = 0.0
            self.v = v_new
            self.a = a
            return self.v

    class QuinticTurn:
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
                ks = KS * sgn(final_err)
            volts = TURN_FF_SCALE * (KV * side_w + KA * side_a) + ks \
                + TURN_KP * err + TURN_KI * self.integral + TURN_KD * (self.w_ref - self.rate)
            if tau >= 1.0 and abs(final_err) < TURN_TOL_DEG and abs(self.rate) < TURN_SETTLE_DPS:
                self.good_loops += 1
            else:
                self.good_loops = 0
            done = self.good_loops >= SETTLE_LOOPS or t > self.timeout
            return volts, done

    def drive_profile(d, vmax, a, jerk_time, dt):
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
            scale = d / total
            out = [x * scale for x in out]
        return out

    def button_by_name(name):
        if name is None:
            return None
        return getattr(controller_1, "button" + name)

    def fn_held():
        return fn_btn is not None and fn_btn.pressing()

    def macro_cancelled():
        global macro_abort, fn_let_go
        if not macro_running:
            return False
        if macro_abort:
            return True
        if not fn_held():
            fn_let_go = True
        elif fn_let_go:
            macro_abort = True
        return macro_abort

    def macro_wait(ms):
        end = brain.timer.time(MSEC) + ms
        while brain.timer.time(MSEC) < end:
            if macro_cancelled():
                return
            wait(LOOP_MS, MSEC)

    def macro_lift_wait():
        end = brain.timer.time(MSEC) + LIFT_MOVE_TIMEOUT_SEC * 1000
        while brain.timer.time(MSEC) < end:
            if macro_cancelled():
                return
            if LiftL1.is_done() and LiftL2.is_done() and LiftR1.is_done() and LiftR2.is_done():
                return
            wait(LOOP_MS, MSEC)

    def run_macro(name, steps):
        global macro_running, macro_abort, fn_let_go, auton_heading_target
        if macro_running:
            return
        controller_1.screen.clear_row(1)
        controller_1.screen.set_cursor(1, 1)
        if len(steps) == 0:
            controller_1.screen.print(name + ": empty")
            return
        fn_let_go = False
        macro_abort = False
        macro_running = True
        controller_1.screen.print(name)
        auton_heading_target = imu_rot()
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

    def tip_guard_drive_scale():
        global tip_guard_on
        lift = LiftL1.position(DEGREES)
        if lift > TIP_GUARD_LIFT_DEG:
            tip_guard_on = True
        elif lift < TIP_GUARD_RELEASE_DEG:
            tip_guard_on = False
        if tip_guard_on:
            return TIP_GUARD_DRIVE_SCALE
        return 1.0

    def lift_ramp_toward(current, target, dt):
        ramp = LIFT_RAMP_SEC
        if target == 0:
            ramp = LIFT_RAMP_SEC * (1.0 - LIFT_BRAKE_SCALE)
        if ramp <= 0.001:
            return target
        step = LIFT_DRIVER_SPEED * dt / ramp
        if current < target:
            return min(target, current + step)
        return max(target, current - step)

    def lift_spin_pct(pct):
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
                show_lift_degrees()
                lift_cmd_pct = lift_ramp_toward(lift_cmd_pct, target_pct, dt)
                lift_spin_pct(lift_cmd_pct)
            else:
                lift_cmd_pct = 0.0
                lift_stop_hold()
            wait(5, MSEC)

    def lift_driver_release():
        global lift_cmd_pct, lift_ramp_id
        lift_ramp_id += 1
        my_id = lift_ramp_id
        last_ms = brain.timer.time(MSEC)
        while lift_cmd_pct != 0 and my_id == lift_ramp_id:
            pos = LiftL1.position(DEGREES)
            if (lift_cmd_pct > 0 and pos > 900) or (lift_cmd_pct < 0 and pos <= 0):
                break
            now = brain.timer.time(MSEC)
            dt = (now - last_ms) / 1000.0
            last_ms = now
            lift_cmd_pct = lift_ramp_toward(lift_cmd_pct, 0.0, dt)
            if lift_cmd_pct == 0:
                break
            lift_spin_pct(lift_cmd_pct)
            wait(5, MSEC)
        if my_id == lift_ramp_id:
            lift_cmd_pct = 0.0
            lift_stop_hold()

    def show_lift_degrees():
        brain.screen.set_font(FontType.MONO40)
        brain.screen.clear_row(1)
        brain.screen.set_cursor(1, 1)
        brain.screen.print(LiftL1.position(DEGREES))

#--------------------------------------------------------------
    precision_btn = button_by_name(PRECISION_BUTTON)
    fn_btn = button_by_name(FN_BUTTON)

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
                        e = -e
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

    def driver_loop():
        global snap_request
        wait_for_imu()
        snap_request = 0
        dt = LOOP_MS / 1000.0
        turn_a_trac = side_to_dps(A_TRACTION)
        turn_a_motor = side_to_dps(A_MOTOR)
        turn_a_brake = side_to_dps(A_BRAKE * DRIVER_BRAKE_SCALE)
        drive_sh = Shaper(A_TRACTION, A_MOTOR, A_BRAKE * DRIVER_BRAKE_SCALE, V_FREE)
        turn_sh = Shaper(turn_a_trac, turn_a_motor, turn_a_brake, TURN_FREE_DPS)
        drive_L = Ceiling(DRIVE_L0, DRIVE_UNLOCK_IN)
        turn_L = Ceiling(TURN_L0, TURN_UNLOCK_DEG)
        hold_target = None
        snap = None
        while True:
            if macro_running:
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

            if snap is None and snap_request != 0:
                if imu_ok and xd == 0 and xt == 0:
                    snap = QuinticTurn(snap_request, SNAP_MAX_DPS, SNAP_MAX_ACCEL_DPS2)
                    drive_sh.reset(0.0)
                snap_request = 0
            if snap is not None:
                if xd != 0 or xt != 0:
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

            target_v = Pd * Ld * fd * V_FREE
            target_v *= tip_guard_drive_scale()
            target_w = Pt * Lt * ft * TURN_FREE_DPS

            w_cap = (A_LAT / max(abs(drive_sh.v), 1e-3)) * 180.0 / math.pi
            target_w = clamp(target_w, -w_cap, w_cap)

            w = turn_sh.step(target_w, dt)

            fwd_room = max(0.0, V_FREE - abs(dps_to_side(w)))
            target_v = clamp(target_v, -fwd_room, fwd_room)
            if abs(drive_sh.v) > fwd_room:
                drive_sh.v = sgn(drive_sh.v) * fwd_room
            v = drive_sh.step(target_v, dt)

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

    def auton_drive(inches):
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
            while last_i < min(i, n - 1):
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
            volts = KV * v_ref + KA * a_ref + ks
            volts *= direction
            h = 0.0
            if imu_ok:
                h = clamp(DRIVE_HEADING_KP * wrap180(heading - imu_rot()), -DRIVE_HEADING_MAX_V, DRIVE_HEADING_MAX_V)
            set_drive_volts(volts + h, volts - h)
            if i >= n:
                good = SETTLE_LOOPS
            else:
                good = 0
            if good >= SETTLE_LOOPS or t > timeout:
                break
            if macro_cancelled():
                break
            wait(LOOP_MS, MSEC)
        stop_drive(BRAKE)

    def auton_turn(robot_degrees):
        global auton_heading_target
        if not imu_ok:
            brain.screen.clear_screen()
            brain.screen.set_cursor(1, 1)
            brain.screen.print("NO IMU: turn skipped")
            return
        delta = robot_degrees + wrap180(auton_heading_target - imu_rot())
        turn = QuinticTurn(delta, AUTON_TURN_MAX_DPS, AUTON_TURN_ACCEL_DPS2)
        while True:
            volts, done = turn.step()
            set_drive_volts(volts, -volts)
            if done:
                break
            if macro_cancelled():
                break
            wait(LOOP_MS, MSEC)
        stop_drive(BRAKE)
        auton_heading_target = auton_heading_target + robot_degrees

    def Forward_inches(inches):
        auton_drive(inches)

    def Backward_inches(inches):
        auton_drive(-inches)

    def Turn_side_robot_degrees(robot_degrees):
        if AUTON_SIDE == "LEFT":
            auton_turn(-robot_degrees)
        else:
            auton_turn(robot_degrees)

    def claw_set(closed):
        global pneumaticClaw
        if closed:
            output = CLAW_CLOSED_OUTPUT
        else:
            output = not CLAW_CLOSED_OUTPUT
        PneumaticClaw.set(output)
        pneumaticClaw = not output

    def claw_toggle():
        global pneumaticClaw
        if pneumaticClaw:
            PneumaticClaw.set(True)
            pneumaticClaw = False
        else:
            PneumaticClaw.set(False)
            pneumaticClaw = True

    def tilt_toggle():
        global pneumaticTilt
        if pneumaticTilt:
            PneumaticTilt.set(True)
            pneumaticTilt = False
        else:
            PneumaticTilt.set(False)
            pneumaticTilt = True

    def rotate_toggle():
        global pneumaticRotate
        if pneumaticRotate:
            PneumaticRotate.set(True)
            pneumaticRotate = False
        else:
            PneumaticRotate.set(False)
            pneumaticRotate = True

    def lift_up_degrees(degrees, wait_done=True):
        show_lift_degrees()
        LiftR1.set_velocity(50, PERCENT)
        LiftL1.set_velocity(50, PERCENT)
        LiftL2.set_velocity(50, PERCENT)
        LiftR2.set_velocity(50, PERCENT)
        degrees = min(degrees, LIFT_MAX_DEGREES - LiftL1.position(DEGREES))
        if degrees <= 0:
            return
        LiftL1.spin_for(FORWARD, degrees, DEGREES, wait=False)
        LiftR1.spin_for(FORWARD, degrees, DEGREES, wait=False)
        LiftL2.spin_for(FORWARD, degrees, DEGREES, wait=False)
        LiftR2.spin_for(FORWARD, degrees, DEGREES, wait=wait_done)

    def lift_down_degrees(degrees, wait_done=True):
        show_lift_degrees()
        LiftR1.set_velocity(LIFT_DOWN_SPEED, PERCENT)
        LiftL1.set_velocity(LIFT_DOWN_SPEED, PERCENT)
        LiftL2.set_velocity(LIFT_DOWN_SPEED, PERCENT)
        LiftR2.set_velocity(LIFT_DOWN_SPEED, PERCENT)
        degrees = min(degrees, LiftL1.position(DEGREES))
        if degrees <= 0:
            return
        LiftL1.spin_for(REVERSE, degrees, DEGREES, wait=False)
        LiftR1.spin_for(REVERSE, degrees, DEGREES, wait=False)
        LiftL2.spin_for(REVERSE, degrees, DEGREES, wait=False)
        LiftR2.spin_for(REVERSE, degrees, DEGREES, wait=wait_done)

    def Lift_Up_inches(inches, wait_done=True):
        lift_up_degrees(inches * LIFT_DEG_PER_INCH, wait_done)

    def Lift_Down_inches(inches, wait_done=True):
        lift_down_degrees(inches * LIFT_DEG_PER_INCH, wait_done)

    def auton_setup():
        global auton_start_ms, auton_heading_target
        auton_start_ms = brain.timer.time(MSEC)
        auton_heading_target = imu_rot()
        for motor in DRIVE_MOTORS:
            motor.set_velocity(AUTON_DRIVE_SPEED, PERCENT)
            motor.set_stopping(BRAKE)
            motor.set_timeout(3, SECONDS)
        for motor in LIFT_MOTORS:
            motor.set_position(0, DEGREES)
            motor.set_timeout(LIFT_MOVE_TIMEOUT_SEC, SECONDS)

    def auton_finish():
        for motor in LIFT_MOTORS:
            motor.stop()
        for motor in DRIVE_MOTORS:
            motor.stop()
            motor.set_stopping(COAST)
        auton_seconds = (brain.timer.time(MSEC) - auton_start_ms) / 1000
        brain.screen.set_cursor(3, 1)
        brain.screen.print("Auton " + str(round(auton_seconds, 1)) + "s")
        print("Auton took " + str(round(auton_seconds, 1)) + " s")

    def on_up():
        fn_arrow("Up")

    def on_left():
        fn_arrow("Left")

    def on_right():
        fn_arrow("Right")

    def on_down():
        if fn_arrow("Down"):
            return
        rotate_toggle()

    def on_x():
        if fn_held():
            macro_x()

    def on_y():
        if fn_held():
            macro_y()
            return
        tilt_toggle()

    def on_a():
        if fn_held():
            macro_a()

    def on_r1_press():
        RearSpinner.spin(REVERSE)

    def on_r1_release():
        RearSpinner.stop()

    def on_l1_press():
        lift_driver_hold(controller_1.buttonL1, LIFT_DRIVER_SPEED)

    def on_l2_press():
        lift_driver_hold(controller_1.buttonL2, -LIFT_DRIVER_SPEED)

    def on_l1_release():
        lift_driver_release()

    def on_l2_release():
        lift_driver_release()

# 4. AUTON
#--------------------------------------------------------------

def run_autonomous():
    wait_for_imu()
    auton_setup()
    if AUTON_TEST != "NONE":
        run_auton_test()
        auton_finish()
        return
    claw_set(True)
    wait(800, MSEC)
    Lift_Up_inches(6.5)
    Forward_inches(38)
    wait(800, MSEC)
    Turn_side_robot_degrees(9.7)
    wait(800, MSEC)
    Forward_inches(45.5)
    Lift_Down_inches(8)
    wait(800, MSEC)
    claw_set(False)
    wait(500, MSEC)
    Backward_inches(6.5)
    Turn_side_robot_degrees(180)
    Forward_inches(32.5)
    auton_finish()


#--------------------------------------------------------------
# 5. MACROS
#--------------------------------------------------------------

MACRO_X_STEPS = []
MACRO_Y_STEPS = []
MACRO_A_STEPS = []

def macro_x():
    run_macro("macro_x", MACRO_X_STEPS)

def macro_y():
    run_macro("macro_y", MACRO_Y_STEPS)

def macro_a():
    run_macro("macro_a", MACRO_A_STEPS)

def fn_arrow(name):
    global snap_request
    if not fn_held():
        return False
    if name == FN_SNAP_LEFT:
        snap_request = -SNAP_DEG
    elif name == FN_SNAP_RIGHT:
        snap_request = SNAP_DEG
    return True


#--------------------------------------------------------------
# 6. Startup
#--------------------------------------------------------------

def startup():
    LiftR1.set_stopping(HOLD)
    LiftR2.set_stopping(HOLD)
    LiftL1.set_stopping(HOLD)
    LiftL2.set_stopping(HOLD)
    LiftR1.set_max_torque(100, PERCENT)
    LiftR2.set_max_torque(100, PERCENT)
    LiftL1.set_max_torque(100, PERCENT)
    LiftL2.set_max_torque(100, PERCENT)
    RearSpinner.set_velocity(40, PERCENT)
    RearSpinner.set_max_torque(100, PERCENT)
    RearSpinner.set_stopping(HOLD)
    for motor in DRIVE_MOTORS:
        motor.set_max_torque(100, PERCENT)
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

controller_1.buttonUp.pressed(on_up)
controller_1.buttonLeft.pressed(on_left)
controller_1.buttonRight.pressed(on_right)
controller_1.buttonDown.pressed(on_down)
controller_1.buttonB.pressed(claw_toggle)
controller_1.buttonX.pressed(on_x)
controller_1.buttonY.pressed(on_y)
controller_1.buttonA.pressed(on_a)
controller_1.buttonR1.pressed(on_r1_press)
controller_1.buttonR1.released(on_r1_release)
controller_1.buttonL1.pressed(on_l1_press)
controller_1.buttonL2.pressed(on_l2_press)
controller_1.buttonL1.released(on_l1_release)
controller_1.buttonL2.released(on_l2_release)

wait(15, MSEC)

startup()
