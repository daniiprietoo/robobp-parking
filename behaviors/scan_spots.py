from utils.state import Spot, StateManager
import time
from robobopy.utils.IR import IR
from robobopy.utils.QRCode import QRCode
from behaviors.behaviors import Behaviour
from robobopy.Robobo import Robobo
from utils.config import (
    SPEED_MEDIUM,
    SPEED_SLOW,
    TILT_CENTER,
    PAN_CENTER,
    PAN_MOVEMENT_SPEED,
    SPEECH_WAIT_TIME,
)


class ScanSpots(Behaviour):
    def __init__(self, robot: Robobo, supress_list, params: StateManager):
        super().__init__(robot, supress_list, params)

        self.max_spots = 4  # Maximum number of parking spots to scan

    def take_control(self) -> bool:
        current_action = self.params.get("current_action")
        parking_state = self.params.get("parking_state", "scanning")
        scanning_complete = self.params.get("scanning_complete", False)

        if current_action == "scan_spots" or (
            parking_state == "scanning" and not scanning_complete
        ):
            if parking_state == "scanning":
                return True

        return False

    # Method that defines what the behavior does
    def action(self):
        print("----> control: ScanSpots")

        self.params.set("current_action_status", "executing")

        self.robot.sayText("I am scanning spots", True)

        self.robot.moveTiltTo(TILT_CENTER, PAN_MOVEMENT_SPEED, True)

        speed = SPEED_SLOW
        self.robot.moveWheels(speed, speed)
        self.robot.startQrTracking()
        pan_positions = [90, -90]
        current_pan_index = 0
        self.robot.movePanTo(
            pan_positions[current_pan_index], PAN_MOVEMENT_SPEED, False
        )

        current_time_pan_move = time.time()

        iteration = 0
        while (
            not self.stopped()
            and len(self.params.get_detected_spots()) < self.max_spots
            and self.params.get("current_action") == "scan_spots"
        ):
            # pan_angle = pan_positions[current_pan_index]
            # current_angle = self.robot.readPanPosition()
            # print(f"Current pan angle: {current_angle}, Target pan angle: {pan_angle}")
            # if abs(current_angle - pan_angle) > 2:
            #     pass
            # else:
            #     current_pan_index = (current_pan_index + 1) % len(pan_positions)
            #     pan_angle = pan_positions[current_pan_index]
            #     self.robot.movePanTo(pan_angle, PAN_MOVEMENT_SPEED, False)

            # Every 2 seconds, move Pan to opposite side
            if time.time() - current_time_pan_move > 4:
                current_pan_index = (current_pan_index + 1) % len(pan_positions)
                pan_angle = pan_positions[current_pan_index]
                self.robot.movePanTo(pan_angle, PAN_MOVEMENT_SPEED, False)
                current_time_pan_move = time.time()

            qr = self.robot.readQR()
            print(
                f"QR read: id={qr.id if qr else None}, distance={qr.distance if qr else None}, data={qr.p1}, {qr.p2}, {qr.p3}"
            )  # Debug

            if qr and qr.distance > 0:
                spot_id = qr.id
                # Check if spot is already recorded
                if spot_id == "rotonda":
                    continue
                if spot_id not in self.params.get_detected_spot_ids():
                    spot_taken = self.is_ocuppied(spot_id, 1 if pan_angle < 0 else -1)
                    spot = Spot(
                        id=spot_id,
                        position=(qr.x, qr.y),
                        timestamp=time.time(),
                        occupied=spot_taken,
                        side="left" if pan_angle < 0 else "right",
                    )
                    self.params.add_detected_spot(spot)

                    print(f"Found spot {spot_id}: {spot}")

                    self.robot.moveWheels(speed, speed)  # Continue moving forward
                else:
                    print(f"Spot {spot_id} already recorded.")

            print(f"Scan iteration {iteration} complete.")
            iteration += 1
            # Add a stop condition if needed
            self.robot.wait(0.1)

        self.robot.stopMotors()
        self.robot.movePanTo(PAN_CENTER, PAN_MOVEMENT_SPEED, True)
        self.params.set("scanning_complete", True)
        self.params.set("parking_state", "waiting_for_input")
        self.params.set("current_action_status", "completed")
        time.sleep(SPEECH_WAIT_TIME)  # Wait for the message to be spoken
        self.robot.stopQrTracking()
        self.supress = True

    def is_ocuppied(self, spot_id: str, direction: int) -> bool:
        self.robot.startObjectRecognition()
        self.robot.stopMotors()
        self.robot.sayText(f"Found parking spot {spot_id}", True)
        self.robot.movePanTo(direction * -120, PAN_MOVEMENT_SPEED)
        time.sleep(1)  # Allow time for the pan movement to complete
        obj = self.robot.readDetectedObject()

        self.robot.movePanTo(direction * 90, PAN_MOVEMENT_SPEED, True)

        self.robot.stopObjectRecognition()
        print(f"Detected object: {obj.label}")
        spot_taken = False
        print(f"Detected object: {obj.label} with confidence {obj.confidence}")
        if obj.label == "robobo" or obj.label == "person":
            spot_taken = True
        return spot_taken
