from utils.state import Spot, StateManager
import time
from robobopy.utils.IR import IR
from robobopy.utils.Sounds import Sounds
from behaviors.behaviors import Behaviour
from robobopy.Robobo import Robobo


class ScanSpots(Behaviour):
    def __init__(self, robot: Robobo, supress_list, params: StateManager):
        super().__init__(robot, supress_list, params)

        self.max_spots = 2  # Maximum number of parking spots to scan

    def take_control(self) -> bool:
        current_action = self.params.get("current_action")
        parking_state = self.params.get("parking_state", "scanning")
        scanning_complete = self.params.get("scanning_complete", False)

        if current_action == "scan_spots" or (parking_state == "scanning" and not scanning_complete):
            if parking_state == "scanning":
                return True
            
        return False

    # Method that defines what the behavior does
    def action(self):
        print("----> control: ScanSpots")

        self.params.set("current_action_status", "executing")

        self.robot.sayText("I am scanning spots")

        self.robot.moveTiltTo(90, 100, True)

        speed = 7
        self.robot.moveWheels(speed, speed)  

        pan_positions = [70, -70]
        current_pan_index = 0
        while (
            not self.stopped()
            and len(self.params.get_detected_spots()) < self.max_spots
            and self.params.get("current_action") == "scan_spots"
        ):
            pan_angle = pan_positions[current_pan_index]
            self.robot.movePanTo(pan_angle, 100, True)
            time.sleep(0.1)
            qr = self.robot.readQR()
            print(
                f"QR read: id={qr.id if qr else None}, distance={qr.distance if qr else None}"
            )  # Debug

            if qr and qr.distance > 0:
                spot_id = qr.id
                # Check if spot is already recorded
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
                else:
                    print(f"Spot {spot_id} already recorded.")

                self.robot.moveWheels(speed, speed)  # Continue moving forward
            # Add a stop condition if needed
            current_pan_index = (current_pan_index + 1) % len(pan_positions)
            time.sleep(0.2)

        self.robot.stopMotors()
        self.robot.movePanTo(0, 100, True)
        self.params.set("scanning_complete", True)
        self.params.set("parking_state", "waiting_for_input")
        self.params.set("current_action_status", "completed")
        time.sleep(2)  # Wait for the message to be spoken
        self.supress = True

    def is_ocuppied(self, spot_id: str, direction: int) -> bool:
        self.robot.startObjectRecognition()
        self.robot.stopMotors()
        self.robot.sayText(f"Found parking spot {spot_id}")
        time.sleep(2)  # Wait for the message to be spoken

        self.robot.movePanTo(direction * -130, 100, True)
        time.sleep(1)  # Allow time for the pan movement to complete
        obj = self.robot.readDetectedObject()

        self.robot.movePanTo(0, 100, True)

        self.robot.stopObjectRecognition()
        print(f"Detected object: {obj.label}")
        spot_taken = False
        print(f"Detected object: {obj.label} with confidence {obj.confidence}")
        if obj.label == "robobo" or obj.label == "person":
            spot_taken = True
        return spot_taken
