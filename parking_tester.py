"""
Test script for tuning parking maneuvers.
Allows direct testing of reverse_entry, straighten, and final_adjustment
without running the full behavior system.
"""

from robobopy.Robobo import Robobo
from utils.state import StateManager, Spot
from utils.config import DEFAULT_SIDE, REVERSE_DURATION, SPEED_SLOW, SPEED_FAST
import time


class ParkingTester:
    def __init__(self, robot: Robobo, side: str = "right"):
        self.robot = robot
        self.side = side  # 'left' or 'right'

    def reverse_entry(
        self,
        speed_fast: int = 12,
        speed_slow: int = 5,
        duration: float = REVERSE_DURATION,
        forward_adjust: float = 0.5,
    ):
        """
        Test reverse entry maneuver.

        Args:
            speed_fast: Speed for the faster wheel (outer wheel in turn)
            speed_slow: Speed for the slower wheel (inner wheel in turn)
            duration: Duration for each reverse phase
            forward_adjust: Small forward movement before reversing
        """
        print(
            f"[Test] Reverse entry - side={self.side}, speed_fast={speed_fast}, speed_slow={speed_slow}, duration={duration}"
        )

        self.robot.sayText("Reversing into the spot")
        time.sleep(2)

        # Small forward adjustment
        print(f"[Test] Forward adjust: {forward_adjust}s")
        # self.robot.moveWheelsByTime(speed_slow, speed_slow, forward_adjust)

        # Reverse with turn based on side
        if self.side == DEFAULT_SIDE:  # left
            print(
                f"[Test] Phase 1: Left={-speed_fast}, Right={-speed_slow}, Duration={duration}"
            )
            self.robot.moveWheelsByTime(-speed_fast, -speed_slow, duration)
            print(
                f"[Test] Phase 2: Left={-speed_slow}, Right={-speed_fast}, Duration={duration}"
            )
            self.robot.moveWheelsByTime(-speed_slow, -speed_slow, 0.5)
            self.robot.moveWheelsByTime(-speed_slow, -speed_fast, duration)
        else:  # right
            print(
                f"[Test] Phase 1: Left={-speed_slow}, Right={-speed_fast}, Duration={duration}"
            )
            self.robot.moveWheelsByTime(-speed_slow, -speed_fast, duration)
            print(
                f"[Test] Phase 2: Left={-speed_fast}, Right={-speed_slow}, Duration={duration}"
            )
            self.robot.moveWheelsByTime(-speed_fast, -speed_fast, 0.5)
            self.robot.moveWheelsByTime(-speed_fast, -speed_slow, duration)

        self.robot.stopMotors()
        print("[Test] Reverse entry complete")

    def straighten(self, speed: int = 5, duration: float = 1.0):
        """
        Test straighten maneuver.

        Args:
            speed: Speed for backward movement
            duration: Duration of backward movement
        """
        print(f"[Test] Straighten - speed={speed}, duration={duration}")

        self.robot.sayText("Straightening")
        time.sleep(1)

        self.robot.moveWheelsByTime(-speed, -speed, duration)
        self.robot.stopMotors()
        print("[Test] Straighten complete")

    def final_adjust(self, speed: int = 5, duration: float = 1.0):
        """
        Test final adjustment maneuver.

        Args:
            speed: Speed for forward movement
            duration: Duration of forward movement
        """
        print(f"[Test] Final adjust - speed={speed}, duration={duration}")

        self.robot.sayText("Final adjustment")
        time.sleep(1)

        self.robot.moveWheelsByTime(speed, speed, duration)
        self.robot.stopMotors()
        print("[Test] Final adjust complete")

    def full_parking_sequence(self, **kwargs):
        """Run the full parking sequence with custom parameters."""
        print("\n" + "=" * 60)
        print("FULL PARKING SEQUENCE")
        print("=" * 60 + "\n")

        self.reverse_entry(
            speed_fast=kwargs.get("reverse_speed_fast", 12),
            speed_slow=kwargs.get("reverse_speed_slow", 5),
            duration=kwargs.get("reverse_duration", REVERSE_DURATION),
            forward_adjust=kwargs.get("forward_adjust", 0.5),
        )
        time.sleep(1)

        self.straighten(
            speed=kwargs.get("straighten_speed", 5),
            duration=kwargs.get("straighten_duration", 1.0),
        )
        time.sleep(1)

        self.final_adjust(
            speed=kwargs.get("final_speed", 5),
            duration=kwargs.get("final_duration", 1.0),
        )

        print("\n" + "=" * 60)
        print("PARKING COMPLETE")
        print("=" * 60 + "\n")


def interactive_menu(tester: ParkingTester):
    """Interactive menu for testing different maneuvers."""
    while True:
        print("\n" + "=" * 60)
        print(f"PARKING TEST MENU (Side: {tester.side})")
        print("=" * 60)
        print("1. Reverse Entry (default params)")
        print("2. Reverse Entry (custom params)")
        print("3. Straighten")
        print("4. Final Adjustment")
        print("5. Full Parking Sequence")
        print("6. Toggle Side (left/right)")
        print("7. Custom Movement Test")
        print("q. Quit")
        print("=" * 60)

        choice = input("Select option: ").strip().lower()

        if choice == "1":
            tester.reverse_entry()

        elif choice == "2":
            try:
                speed_fast = int(input("Speed fast (default 12): ") or "12")
                speed_slow = int(input("Speed slow (default 5): ") or "5")
                duration = float(input("Duration per phase (default 3.5): ") or "3.5")
                forward = float(input("Forward adjust (default 0.5): ") or "0.5")
                tester.reverse_entry(speed_fast, speed_slow, duration, forward)
            except ValueError:
                print("Invalid input, using defaults")
                tester.reverse_entry()

        elif choice == "3":
            try:
                speed = int(input("Speed (default 5): ") or "5")
                duration = float(input("Duration (default 1.0): ") or "1.0")
                tester.straighten(speed, duration)
            except ValueError:
                tester.straighten()

        elif choice == "4":
            try:
                speed = int(input("Speed (default 5): ") or "5")
                duration = float(input("Duration (default 1.0): ") or "1.0")
                tester.final_adjust(speed, duration)
            except ValueError:
                tester.final_adjust()

        elif choice == "5":
            tester.full_parking_sequence()

        elif choice == "6":
            tester.side = "left" if tester.side == "right" else "right"
            print(f"Side changed to: {tester.side}")

        elif choice == "7":
            try:
                left = int(input("Left wheel speed: "))
                right = int(input("Right wheel speed: "))
                duration = float(input("Duration (seconds): "))
                print(f"[Test] Custom: Left={left}, Right={right}, Duration={duration}")
                tester.robot.moveWheelsByTime(left, right, duration)
                tester.robot.stopMotors()
            except ValueError:
                print("Invalid input")

        elif choice == "q":
            break

        else:
            print("Invalid option")


def main():
    print("=" * 60)
    print("PARKING MANEUVER TEST SCRIPT")
    print("Target Spot: 8 (right side)")
    print("=" * 60)

    # Connect to robot
    robot = Robobo("localhost")
    print("Connecting to robot...")
    robot.connect()
    print("Connected!")

    # Create tester with spot 8 settings (right side)
    tester = ParkingTester(robot, side="right")

    try:
        # Run interactive menu
        interactive_menu(tester)

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    finally:
        robot.stopMotors()
        robot.sayText("Test complete")
        time.sleep(2)
        robot.disconnect()
        print("Disconnected from robot")


if __name__ == "__main__":
    main()
