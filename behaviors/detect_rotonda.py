from behaviors.behaviors import Behaviour
from robobopy.utils.IR import IR
from utils.state import StateManager
import time


class DetectRotonda(Behaviour):
    """
    Behavior that detects the "rotonda" sign and performs a 180-degree turn
    when the robot is close enough to it.
    """
    
    def __init__(self, robot, supress_list, params: StateManager):
        super().__init__(robot, supress_list, params)
        self.rotonda_detected = False
        # Distance is in METERS according to Robobo API documentation
        self.min_distance = 0.3  # Minimum distance in meters to trigger turn (30 cm)
        self.max_distance = 1.0  # Maximum distance in meters to consider detection valid (100 cm)

    def take_control(self) -> bool:
        """Take control when approaching a parking spot and rotonda hasn't been detected yet."""
        parking_state = self.params.get("parking_state", "searching")
        rotonda_detected = self.params.get("rotonda_detected", False)
        
        # Active during approach phase and rotonda not yet detected
        # This behavior has high priority and can interrupt others
        if parking_state == "approaching" and not rotonda_detected:
            # Check if we can actually detect rotonda (quick check)
            # This allows the behavior to take control even if slightly suppressed
            return True
        return False

    def action(self):
        """Continuously check for 'rotonda' sign and perform turn when detected."""
        print("----> control: DetectRotonda (monitoring for rotonda)")
        self.supress = False
        
        # Don't suppress FindQR initially - let it move the robot
        # We'll only take full control when rotonda is detected
        # Suppress only scan_spots to avoid interference
        for bh in self.supress_list:
            if isinstance(bh, type(self)) or "ScanSpots" in str(type(bh)):
                bh.supress = True

        # Ensure camera is positioned to read signs
        self.robot.moveTiltTo(90, 100, True)
        self.robot.movePanTo(0, 100, True)
        
        # Check for rotonda sign continuously
        # This behavior monitors while FindQR controls movement
        while not self.stopped():
            # Check if we should still be looking for rotonda
            parking_state = self.params.get("parking_state", "searching")
            if parking_state != "approaching":
                break
                
            if self.params.get("rotonda_detected", False):
                break
            
            # Check QR codes for "rotonda" sign
            # Note: Robobo doesn't have text recognition, so we use QR codes
            # The "rotonda" sign should be encoded as a QR code with "rotonda" in its ID
            qr = self.robot.readQR()
            detected_text = None
            distance = None
            
            if qr and qr.id is not None:
                # QR id is an int according to Robobo API, convert to string for comparison
                qr_id_str = str(qr.id).lower()
                if "rotonda" in qr_id_str:
                    detected_text = "rotonda"
                    distance = qr.distance  # Distance is in meters
            
            # If "rotonda" is detected and we're close enough
            if detected_text and "rotonda" in detected_text:
                if distance is not None:
                    print(f"[DetectRotonda] Detected 'rotonda' at distance: {distance} meters")
                    
                    # Check if we're within the valid distance range
                    if self.min_distance <= distance <= self.max_distance:
                        print(f"[DetectRotonda] Close enough! Taking control and performing 180-degree turn...")
                        # Now suppress FindQR to take full control
                        for bh in self.supress_list:
                            bh.supress = True
                        self.robot.stopMotors()
                        self.perform_180_turn()
                        self.params.set("rotonda_detected", True)
                        self.robot.sayText("Rotonda detected, turning around")
                        break
                    elif distance < self.min_distance:
                        # Too close, might have missed it or already passed
                        print(f"[DetectRotonda] Too close ({distance} m), might have passed the sign")
                    else:
                        # Still too far
                        print(f"[DetectRotonda] Still too far ({distance} m), continuing to monitor...")
                else:
                    # Distance not available, but rotonda QR detected - perform turn anyway
                    print(f"[DetectRotonda] 'Rotonda' QR detected but distance unknown. Taking control and performing turn...")
                    # Now suppress FindQR to take full control
                    for bh in self.supress_list:
                        bh.supress = True
                    self.robot.stopMotors()
                    self.perform_180_turn()
                    self.params.set("rotonda_detected", True)
                    self.robot.sayText("Rotonda detected, turning around")
                    break
            
            time.sleep(0.1)  # Small delay to avoid excessive CPU usage

    def perform_180_turn(self):
        """
        Perform a 180-degree turn in place.
        Uses moveWheelsByTime for precise control.
        Left wheel moves backward, right wheel moves forward to turn left.
        """
        print("[DetectRotonda] Starting 180-degree turn...")
        
        # Rotate left wheel backward, right wheel forward to turn left
        # Speed: positive = forward, negative = backward
        turn_speed = 15  # Speed factor [-100..100]
        # Approximate time for 180-degree turn (adjust based on robot characteristics)
        # This may need calibration based on your specific robot
        turn_time = 2.5  # seconds (adjust based on your robot's turning speed)
        
        # Use moveWheelsByTime for blocking, precise turn
        # Left wheel backward (-), right wheel forward (+) = turn left
        self.robot.moveWheelsByTime(-turn_speed, turn_speed, turn_time, wait=True)
        
        print("[DetectRotonda] 180-degree turn completed")



