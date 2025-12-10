from robobopy.utils.IR import IR
from behaviors.behaviors import Behaviour
from robobopy.Robobo import Robobo
from utils.config import DEFAULT_SIDE, REVERSE_DURATION
import time
from utils.state import StateManager


class Parking(Behaviour):
    def __init__(self, robot: Robobo, supress_list, params: StateManager):
        super().__init__(robot, supress_list, params)
        self._is_executing = False  # Track if we're currently executing

    def take_control(self) -> bool:
        if self._is_executing:
            return False
        if self.params.get("target_spot") is not None:
            current_action = self.params.get("current_action")
            current_status = self.params.get("current_action_status")
            if current_status is "completed":
                return False
            return current_action in ["reverse_entry", "final_adjustment", "straighten"]
        return False

    # Method that defines what the behavior does
    def action(self):
        self._is_executing = True
        try:
            print("----> control: Parking")  # Log activation
            current_action = self.params.get("current_action")

            self.params.set("current_action_status", "executing")

            # Notify the user that the robot is parking
            self.robot.sayText("Parking now")
            time.sleep(2)  # Wait for the message to be spoken

            if current_action == "reverse_entry":
                self._reverse_entry()
            elif current_action == "straighten":
                self._straighten()
            elif current_action == "final_adjustment":
                self._final_adjust()
            else:
                print(f"[Parking] Unknown action: {current_action}")
                self.params.set("current_action_status", "failed")
                return
            self.robot.wait(0.1)
        finally:
            self._is_executing = False

    def _get_side(self):
        target_spot_info = self.params.get_target_spot_info()
        if target_spot_info is not None:
            return target_spot_info.side  # 'left' or 'right'
        else:
            print(
                "[Parking] Warning: Target spot info not found, defaulting to left side."
            )
            return "left"  # Default to left if not found

    def _reverse_entry(self):
        self.robot.sayText("Reversing into the spot")
        print("[Parking] Reversing into the spot")
        self.robot.wait(2)
        side = self._get_side()

        # self.robot.moveWheelsByTime(5, 5, 0.5)
        # Start reversing depending on side
        if side == DEFAULT_SIDE:
            self.robot.moveWheelsByTime(-14, -5, REVERSE_DURATION)
            self.robot.moveWheelsByTime(-10, -10, 0.5)
            self.robot.moveWheelsByTime(-5, -14, REVERSE_DURATION)
        else:
            self.robot.moveWheelsByTime(-5, -14, REVERSE_DURATION)
            self.robot.moveWheelsByTime(-10, -10, 0.5)
            self.robot.moveWheelsByTime(-14, -5, REVERSE_DURATION)
        self.params.set("current_action_status", "completed")

    def _straighten(self):
        self.robot.sayText("Straightening the robot")
        print("[Parking] Straightening the robot")

        side = self._get_side()

        # Small backward movement to ensure fully in spot
        self.robot.moveWheelsByTime(10, 10, 2)
        self.robot.stopMotors()

        self.params.set("current_action_status", "completed")

    def _final_adjust(self):
        self.robot.sayText("Final adjustment")
        print("[Parking] Performing final adjustment")

        side = self._get_side()

        # Small forward movement to adjust position
        # self.robot.moveWheelsByTime(5, 5, 1)
        self.robot.stopMotors()

        self.params.set("current_action_status", "completed")
