from dataclasses import dataclass
from threading import Lock
from typing import Optional


@dataclass
class Spot:
    id: str
    position: tuple  # (x, y) coordinates
    timestamp: float
    occupied: bool
    side: str  # 'left' or 'right'


class StateManager:
    """
    Manages shared state between behaviors in a thread-safe manner.
    """

    def __init__(self):
        self._lock = Lock()
        self._state = {
            "stop": False,
            "parking_spots": [],  # List of {id, qr_code, position, timestamp, occupied}
            "target_spot": None,  # Selected spot to park in {id, qr_code, position}
            "parking_state": "scanning",  # searching, scanning, waiting_for_input, approaching, parking, aligned, done
            "obstacle_detected": False,
            "current_phase": None, 
            "parking_parameters": None, 
            "emergency_stop": False,  # Emergency stop flag
            "scanning_complete": False,  # True when all spots have been scanned
            "rotonda_detected": False,  # True when "rotonda" sign has been detected and turn completed
            "current_plan": None,  # Current plan being executed
            "current_step_index": 0,  # Current step index in the plan
            "replan_needed": False,  # Flag to indicate if replanning is needed
            "replan_reason": None,  # Reason for replanning
            "current_action": None,  # Current action being executed
            "current_action_params": None,  # Parameters for the current action
            "current_action_status": None,  # Status of the current action (e.g., "executing", "completed", "failed")
        }

    def get(self, key, default=None):
        """Get a state value in a thread-safe manner."""
        with self._lock:
            return self._state.get(key, default)

    def set(self, key, value):
        """Set a state value in a thread-safe manner."""
        with self._lock:
            self._state[key] = value

    def update(self, updates):
        """Update multiple state values at once in a thread-safe manner."""
        with self._lock:
            self._state.update(updates)

    def get_all(self):
        """Get all state in a thread-safe manner (returns a copy)."""
        with self._lock:
            return self._state.copy()

    def add_detected_spot(self, spot_data: Spot):
        """Add a detected parking spot to the list."""
        with self._lock:
            # Check if spot already exists (by id)
            for i, spot in enumerate(self._state["parking_spots"]):
                if spot.id == spot_data.id:
                    # Update existing spot
                    self._state["parking_spots"][i] = spot_data
                    return
            # Add new spot
            self._state["parking_spots"].append(spot_data)
            # Sort by id
            self._state["parking_spots"].sort(key=lambda x: int(x.id or "0"))

    def clear_detected_spots(self):
        """Clear all detected spots."""
        with self._lock:
            self._state["parking_spots"] = []

    def get_detected_spots(self):
        """Get list of detected spots."""
        with self._lock:
            return self._state["parking_spots"].copy()

    def get_detected_spot_ids(self):
        """Get list of detected spot IDs."""
        with self._lock:
            return [spot.id for spot in self._state["parking_spots"]]

    def get_target_spot_info(self) -> Optional[Spot]:
        """Get the currently selected target spot."""
        with self._lock:
            for i in self._state["parking_spots"]:
                if i.id == self._state["target_spot"]:
                    return i
            return None
