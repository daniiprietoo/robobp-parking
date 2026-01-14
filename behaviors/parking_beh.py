from robobopy.utils.IR import IR
from behaviors.behaviors import Behaviour
from robobopy.Robobo import Robobo
from utils.config import (
    DEFAULT_SIDE,
    FAST_WHEEL_SPEED,
    REVERSE_DURATION,
    SLOW_WHEEL_SPEED,
    SPEECH_WAIT_TIME,
)
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
            if current_status == "completed":
                return False
            return current_action in ["reverse_entry", "final_adjustment", "straighten"]
        return False

    def action(self):
        self.supress = False
        self.suppress_others()
        self._is_executing = True
        parking_maneuver = (
            "forward" if self.params.get("rotonda_detected") else "reverse"
        )
        try:
            print("----> control: Parking")
            current_action = self.params.get("current_action")

            self.params.set("current_action_status", "executing")

            if current_action == "reverse_entry":
                self.robot.sayText("Parking now", True)
                if parking_maneuver == "forward":
                    self._forward_entry()
                else:
                    self._reverse_entry()
            elif current_action == "straighten":
                self._straighten()
            elif current_action == "final_adjustment":
                if parking_maneuver == "forward":
                    self._final_adjust_back()
                else:
                    self.final_adjust_front()
            else:
                print(f"[Parking] Unknown action: {current_action}")
                self.params.set("current_action_status", "failed")
                return
            self.robot.wait(0.5)
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
        self.robot.sayText("Reversing into the spot", True)
        print("[Parking] Reversing into the spot")
        side = self._get_side()

        # self.robot.moveWheelsByTime(5, 5, 0.5)
        # Start reversing depending on side
        if side == DEFAULT_SIDE:
            self.robot.moveWheelsByTime(
                -FAST_WHEEL_SPEED, -SLOW_WHEEL_SPEED, REVERSE_DURATION, True
            )
            self.robot.moveWheelsByTime(-10, -10, 0.8, True)
            self.robot.moveWheelsByTime(
                -SLOW_WHEEL_SPEED, -FAST_WHEEL_SPEED, REVERSE_DURATION, True
            )
        else:
            self.robot.moveWheelsByTime(
                -SLOW_WHEEL_SPEED, -FAST_WHEEL_SPEED, REVERSE_DURATION, True
            )
            self.robot.moveWheelsByTime(-10, -10, 0.8, True)
            self.robot.moveWheelsByTime(
                -FAST_WHEEL_SPEED, -SLOW_WHEEL_SPEED, REVERSE_DURATION, True
            )
        self.params.set("current_action_status", "completed")

    def _forward_entry(self):
        self.robot.sayText("Moving forward into the spot", True)
        print("[Parking] Moving forward into the spot")
        self.robot.wait(SPEECH_WAIT_TIME)
        side = self._get_side()

        # Start moving forward depending on side
        if side == DEFAULT_SIDE:
            self.robot.moveWheelsByTime(
                FAST_WHEEL_SPEED, SLOW_WHEEL_SPEED, REVERSE_DURATION, True
            )
            self.robot.moveWheelsByTime(10, 10, 0.8, True)
            self.robot.moveWheelsByTime(
                SLOW_WHEEL_SPEED, FAST_WHEEL_SPEED, REVERSE_DURATION, True
            )
        else:
            self.robot.moveWheelsByTime(
                SLOW_WHEEL_SPEED, FAST_WHEEL_SPEED, REVERSE_DURATION, True
            )
            self.robot.moveWheelsByTime(10, 10, 0.8, True)
            self.robot.moveWheelsByTime(
                FAST_WHEEL_SPEED, SLOW_WHEEL_SPEED, REVERSE_DURATION, True
            )
        self.params.set("current_action_status", "completed")

    def _straighten(self):
        """Currently doees nothing"""
        # self.robot.sayText("Straightening the robot", True)
        print("[Parking] Straightening the robot")

        self.params.set("current_action_status", "completed")

    def _final_adjust_back(self):
        self.robot.sayText("Final adjustment backward", True)
        print("[Parking] Performing final adjustment backward")

        side = self._get_side()

        # Small forward movement to adjust position
        self.robot.moveWheels(-5, -5)
        while self.robot.readIRSensor(IR.BackC) < 80:
            self.robot.wait(0.2)
            if self.stopped():
                break
        self.robot.stopMotors()

        self.params.set("current_action_status", "completed")

    def final_adjust_front(self):
        self.robot.sayText("Final adjustment backward", True)
        print("[Parking] Performing final adjustment forward")

        side = self._get_side()

        # Small forward movement to adjust position
        self.robot.moveWheels(5, 5)
        while self.robot.readIRSensor(IR.FrontC) < 80:
            self.robot.wait(0.2)
            if self.stopped():
                break
        self.robot.stopMotors()

        self.params.set("current_action_status", "completed")
        time.sleep(0.5)
