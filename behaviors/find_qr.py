from webbrowser import get
from behaviors.behaviors import Behaviour
from robobopy.utils.IR import IR
from robobopy.utils.Wheels import Wheels
from utils.state import StateManager
import time


class FindQR(Behaviour):
    """
    Behavior for the robot to find, aproach, center, and stop at a QRcode.
    """

    def __init__(self, robot, supress_list, params: StateManager):
        # Initialize the GoToWall behavior
        super().__init__(robot, supress_list, params)

    # Method that defines when the behavior should take control
    def take_control(self) -> bool:
        if not self.supress:
            current_action = self.params.get("current_action")
            return current_action == "find_spot_qr"
        
        return False

    def action(self):
        print("----> control: FindQR")
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
        time.sleep(1)

        # 2) Determine side and orient camera
        speed = 5
        target_spot_info = self.params.get_target_spot_info()
        if target_spot_info is not None:
            side_of_parking = target_spot_info.side  # 'left' or 'right'
        else:
            side_of_parking = "left"
            print(
                "[FindQR] Warning: Target spot info not found, defaulting to left side."
            )

        self.robot.moveWheels(speed, speed)
        pan_angle = -90 if side_of_parking == "left" else 90
        self.robot.movePanTo(pan_angle, 100, True)

        # 3) Main loop
        rotonda_detected = self.params.get("rotonda_detected", False)
        min_rotonda_distance = 70  # cm (matches your logs)

        while not self.stopped():
            qr = self.robot.readQR()

            if qr and qr.id is not None and qr.distance is not None and qr.distance > 0:
                qr_id_str = str(qr.id).lower()
                distance = qr.distance  # cm

                # --- Rotonda handling (optional, keep simple) ---
                if (not rotonda_detected) and ("rotonda" in qr_id_str):
                    print(
                        f"[FindQR] Detected 'rotonda' QR at distance: {distance:.2f} cm"
                    )
                    if distance >= min_rotonda_distance:
                        print("[FindQR] Close enough! Performing 180-degree turn...")
                        self.robot.stopMotors()
                        self._perform_180_turn()
                        rotonda_detected = True
                        self.params.set("rotonda_detected", True)
                        self.robot.sayText("Rotonda detected, turning around")
                        time.sleep(1)
                        self.robot.moveWheels(speed, speed)
                        side_of_parking = (
                            "right" if side_of_parking == "left" else "left"
                        )
                        pan_angle = -90 if side_of_parking == "left" else 90
                        self.robot.movePanTo(pan_angle, 100, True)

                # --- Target QR detection ---
                if str(qr.id) == target_spot_id:
                    print(
                        f"[FindQR] Detected target QR: {qr.id} at distance {distance:.2f} cm"
                    )
                    self.robot.stopMotors()
                    # Approach & center
                    self._getCloserToPillarAndCentered(target_distance=60)

                    # Mark success and EXIT
                    self.params.set("found_qr", qr)
                    print("[FindQR] Target QR approach and centering completed.")
                    self.params.set("current_action_status", "completed")
                    print("[FindQR] DEBUG: set current_action_status='completed'")
                    self.robot.stopMotors()
                    self.supress = True
                    return  # <<< important

            self.robot.wait(0.1)

        # 4) If we exit the while without success
        print("[FindQR] Target QR not found during approach or behavior stopped.")
        self.params.set("current_action_status", "failed")
        self.robot.stopMotors()

    def _perform_180_turn(self):
        print("[FindQR] Starting 180-degree turn...")

        # Rotate left wheel backward, right wheel forward to turn left
        # Speed: positive = forward, negative = backward
        turn_speed = 5
        t = 3.5
        self.robot.moveWheels(-turn_speed, turn_speed)
        time.sleep(t)
        self.robot.stopMotors()

        print("[FindQR] 180-degree turn completed")

    def _getCloserToPillarAndCentered(self, target_distance=70):
        centered = self._qrIsCentered()
        side = self._get_side()

        mult = 1 if side == "left" else -1

        while True:
            qr = self.robot.readQR()
            if qr and qr.distance > 0:
                print(f"Current distance to pillar: {qr.distance} cm")
                if qr.distance >= target_distance:
                    if self._qrIsCentered():
                        print("Reached target distance to pillar.")
                        self.robot.stopMotors()
                        break
                    else:
                        print("QR not centered, adjusting...")
                        self.robot.moveWheels(10, 10)
                        self.robot.wait(0.2)
                        continue

            print("Performing S-curve maneuver to get closer to pillar...")

            if side == "left":
                self.robot.moveWheelsByTime((-7), (-2), 2)
                self.robot.moveWheelsByTime((-2), (-7), 2)
            else:
                self.robot.moveWheelsByTime((-2), (-7), 2)
                self.robot.moveWheelsByTime((-7), (-2), 2)

            print("Moving forward until centered...")
            self.robot.moveWheels(5, 5)
            while True:
                qr = self.robot.readQR()
                if qr and qr.distance > 0:
                    if self._qrIsCentered(40):
                        print("QR is now centered.")
                        self.robot.stopMotors()
                        break
                self.robot.wait(0.1)

            if qr and qr.distance >= target_distance:
                print("Reached target distance to pillar after adjustments.")
                self.robot.stopMotors()
                break

            self.robot.wait(0.1)

    def _qrIsCentered(self, tolerance=20):
        """Check if the QR code is centered within a tolerance"""
        center = 300  # Assuming 600px width
        qr = self.robot.readQR()
        if qr and qr.distance > 0:
            print(f"QR X position: {qr.x} cm")
            return abs(qr.x - center) <= tolerance
        return False

    def _get_side(self):
        target_spot_info = self.params.get_target_spot_info()
        if target_spot_info is not None:
            return target_spot_info.side  # 'left' or 'right'
        else:
            print(
                "[Parking] Warning: Target spot info not found, defaulting to left side."
            )
            return "left"  # Default to left if not found
