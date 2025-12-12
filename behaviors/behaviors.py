#
# Class that inherits from Thread and manages the threads for behaviors.
# It ensures the architecture operates correctly.
#

from threading import Thread
import time
from robobopy.Robobo import Robobo

from utils.config import LOOP_DELAY
from utils.state import StateManager


class Behaviour(Thread):
    def __init__(
        self,
        robot: Robobo,
        supress_list: list["Behaviour"],
        params: StateManager,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.robot = robot  # Reference to the robot object
        self.__supress = False  # Internal flag for suppression
        self.supress_list = supress_list  # List of behaviors this one can suppress
        self.params = params  # Shared parameters (e.g., mission control)

    # Method to determine if the behavior should take control
    # This should be implemented in subclasses
    def take_control(self) -> bool:
        pass

    # Method defining the behavior's actions
    # This should be implemented in subclasses
    def action(self):
        pass

    # Main thread execution method
    # Continuously checks if the mission is complete or if the behavior
    # should take control, and performs the associated actions
    def run(self):
        while not self.params.get(
            "stop", False
        ):  # Loop until the mission is marked as complete
            # Wait until this behavior takes control or the mission ends
            while not self.take_control() and not self.params.get("stop", False):
                time.sleep(LOOP_DELAY)  # Small delay to reduce CPU usage
            if not self.params.get(
                "stop", False
            ):  # Perform the action if the mission is still ongoing
                self.action()
            time.sleep(LOOP_DELAY)  # Small delay before the next check

    # Property to get the suppression state
    @property
    def supress(self):
        return self.__supress

    # Property setter to update the suppression state
    @supress.setter
    def supress(self, state):
        self.__supress = state

    # Method to signal that the mission should stop
    def set_stop(self):
        self.params.set("stop", True)

    # Method to check if the mission is stopped
    def stopped(self):
        return self.params.get("stop", False)

    def suppress_others(self) -> None:
        """Suppress all behaviors in the suppress list."""
        for behavior in self.supress_list:
            behavior.supress = True

    def release_others(self) -> None:
        """Release suppression on all behaviors in the suppress list."""
        for behavior in self.supress_list:
            behavior.supress = False
