from behaviors.behaviors import Behaviour
from utils.state import StateManager
import time
from utils.config import (
    TURNING_TIME,
    SPEED_SLOW,
    PAN_LEFT,
    PAN_RIGHT,
    PAN_MOVEMENT_SPEED,
    TARGET_DISTANCE_TO_PILLAR,
    QR_CENTER_TOLERANCE,
    SPEECH_WAIT_TIME,
)


class FindQR(Behaviour):
    """
    Behavior for the robot to find, aproach, center, and stop at a QRcode.
    """

    def __init__(self, robot, supress_list, params: StateManager):
        super().__init__(robot, supress_list, params)
        self.rotonda_check_interval = 3
        self.speed = SPEED_SLOW
        self._is_moving = False

    def take_control(self) -> bool:
        if not self.supress:
            current_action = self.params.get("current_action")
            return current_action == "find_spot_qr"

        return False

    def action(self):
        print("----> control: FindQR")
        self.supress = False
        self.suppress_others()
        self._is_moving = False
        # start in executing
        current_status = self.params.get("current_action_status")
        if current_status not in ("completed", "failed"):
            self.params.set("current_action_status", "executing")

        # 1) Resolve target_spot_id from plan params or global state
        action_params = self.params.get("current_action_params") or {}
        plan_target_id = action_params.get("target_spot_id")
        global_target_id = self.params.get("target_spot")

        if plan_target_id is not None:
            target_spot_id = str(plan_target_id)
        elif global_target_id is not None:
            target_spot_id = str(global_target_id)
        else:
            print("[FindQR] ERROR: No target_spot_id specified.")
            self.params.set("current_action_status", "failed")
            return

        print(f"[FindQR] Looking for target spot QR id={target_spot_id}")

        self.robot.sayText("Approaching parking spot")
        time.sleep(SPEECH_WAIT_TIME)

        # 2) Determine side and orient camera
        target_spot_info = self.params.get_target_spot_info()
        if target_spot_info is not None:
            side_of_parking = target_spot_info.side  # 'left' or 'right'
        else:
            side_of_parking = "left"
            print(
                "[FindQR] Warning: Target spot info not found, defaulting to left side."
            )
        self._is_moving = True
        self.robot.moveWheels(self.speed, self.speed)

        pan_angle = PAN_LEFT if side_of_parking == "left" else PAN_RIGHT
        self.robot.movePanTo(pan_angle, PAN_MOVEMENT_SPEED, True)

        # 3) Main loop
        rotonda_detected = self.params.get("rotonda_detected", False)
        self.robot.startQrTracking()
        last_rotonda_check = time.time()

        while not self.stopped():

            if (
                not rotonda_detected
                and (time.time() - last_rotonda_check) >= self.rotonda_check_interval
            ):
                print("[FindQR] Performing periodic rotonda check...")
                self._is_moving = False
                self.robot.stopMotors()
                detected = self._rotonda_check()
                if detected:
                    rotonda_detected = True
                last_rotonda_check = time.time()

            if not self._is_moving:
                self._is_moving = True
                self.robot.moveWheels(self.speed, self.speed)

            qr = self.robot.readQR()
            if qr and qr.id is not None and qr.distance is not None and qr.distance > 0:
                distance = qr.distance  # cm
                # --- Target QR detection ---
                print(f"[FindQR] Detected QR: {qr.id} at distance {distance:.2f} cm")
                if qr.id == target_spot_id:
                    print(
                        f"[FindQR] Detected target QR: {qr.id} at distance {distance:.2f} cm"
                    )
                    self.robot.stopMotors()
                    self._is_moving = False
                    self._getCloserToPillarAndCentered(
                        target_distance=TARGET_DISTANCE_TO_PILLAR
                    )

                    # Mark success and EXIT
                    self.params.set("found_qr", qr)
                    print("[FindQR] Target QR approach and centering completed.")
                    self.params.set("current_action_status", "completed")
                    print("[FindQR] DEBUG: set current_action_status='completed'")
                    self.robot.stopMotors()
                    self.supress = True
                    return

            self.robot.wait(0.1)

        # 4) exit the while without success
        print("[FindQR] Target QR not found during approach or behavior stopped.")
        self.params.set("current_action_status", "failed")
        self.robot.stopQrTracking()
        self.robot.stopMotors()

    def _perform_180_turn(self):
        print("[FindQR] Starting 180-degree turn...")

        # Rotate left wheel backward, right wheel forward to turn left
        turn_speed = self.speed
        self.robot.moveWheelsByTime(-turn_speed, turn_speed, TURNING_TIME, True)
        self.params.invert_sides()
        print("[FindQR] 180-degree turn completed")

    def _getCloserToPillarAndCentered(self, target_distance=TARGET_DISTANCE_TO_PILLAR):
        centered = self._qrIsCentered()
        side = self._get_side()

        mult = 1 if side == "left" else -1
        self.robot.moveWheels(self.speed, self.speed)
        self._is_moving = True

        while True:
            qr = self.robot.readQR()

            # Check distance and centering
            if qr and qr.distance > 0:
                print(f"Current distance to pillar: {qr.distance} cm")
                if qr.distance >= target_distance:
                    if self._qrIsCentered(QR_CENTER_TOLERANCE):
                        print("Reached target distance to pillar.")
                        self._is_moving = False
                        self.robot.stopMotors()
                        break
                    else:
                        print("QR not centered, adjusting...")
                        if not self._is_moving:
                            self.robot.moveWheels(self.speed, self.speed)
                            self._is_moving = True
                        self.robot.wait(0.2)
                        continue

            # if not centered, perform S-curve to center
            print("Performing S-curve maneuver to get closer to pillar...")
            self._is_moving = False
            if side == "left":
                self.robot.moveWheelsByTime((-9), (-2), 2, True)
                self.robot.moveWheelsByTime((-2), (-9), 2, True)
            else:
                self.robot.moveWheelsByTime((-2), (-9), 2, True)
                self.robot.moveWheelsByTime((-9), (-2), 2, True)

            print("Moving forward until centered...")

            # Move forward until centered
            if not self._is_moving:
                self.robot.moveWheels(self.speed, self.speed)
                self._is_moving = True
            while True:
                qr = self.robot.readQR()
                if qr and qr.distance > 0:
                    if self._qrIsCentered(QR_CENTER_TOLERANCE):
                        print("QR is now centered.")
                        self._is_moving = False
                        self.robot.stopMotors()
                        break
                self.robot.wait(0.1)

            if qr and qr.distance >= target_distance:
                print("Reached target distance to pillar after adjustments.")
                self.robot.stopMotors()
                break

            self.robot.wait(0.2)

    def _qrIsCentered(self, tolerance=QR_CENTER_TOLERANCE):
        """Check if the QR code is centered within a tolerance"""
        center = 200  # Assuming 600px width
        qr = self.robot.readQR()
        if qr and qr.distance > 0:
            print(f"QR X position: {qr.x} cm")
            return abs(qr.x - center) <= tolerance
        return False

    def _get_side(self):
        """
        Determine the side ('left' or 'right') of the target parking spot.
        """
        target_spot_info = self.params.get_target_spot_info()
        if target_spot_info is not None:
            return target_spot_info.side  # 'left' or 'right'
        else:
            print(
                "[Parking] Warning: Target spot info not found, defaulting to left side."
            )
            return "left"  # Default to left if not found

    def _rotonda_check(self):
        """Periodic check for 'rotonda' QR code"""
        self.robot.movePanTo(0, PAN_MOVEMENT_SPEED, True)

        rotonda = False
        qr = self.robot.readQR()
        if qr and qr.id is not None and qr.distance is not None and qr.distance > 0:
            distance = qr.distance

            if "rotonda" in qr.id:
                print(
                    f"[FindQR] Detected 'rotonda' QR at distance: {distance:.2f} cm during rotonda check"
                )
                if distance >= 50:
                    print("[FindQR] Close enough! Performing 180-degree turn...")
                    self.robot.sayText("Rotonda detected, turning around", True)
                    self._perform_180_turn()
                    self.params.set("rotonda_detected", True)
                    rotonda = True
                    time.sleep(SPEECH_WAIT_TIME)
        # Reorient camera to side
        side_of_parking = self._get_side()
        pan_angle = PAN_LEFT if side_of_parking == "left" else PAN_RIGHT
        self.robot.movePanTo(pan_angle, PAN_MOVEMENT_SPEED, True)
        return rotonda
