from typing import Any, Optional


class Plan:

    def __init__(self, steps: list[dict[str, Any]]):
        """
        steps:
        {
            "action": str,
            "parameters": dict[str, Any],
            "status": str  # "pending", "in_progress", "completed", "failed"
            "completed": bool
        }
        """
        self.steps = steps
        self.current_step_index = 0

    def get_next_step(self) -> dict[str, Any] | None:
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def mark_step_completed(self, step_index: int):
        if 0 <= self.current_step_index < len(self.steps):
            self.steps[self.current_step_index]["status"] = "completed"
            self.steps[self.current_step_index]["completed"] = True
            self.current_step_index += 1

    def mark_step_failed(self, step_index: int, reason: str = ""):
        if 0 <= self.current_step_index < len(self.steps):
            self.steps[self.current_step_index]["status"] = "failed"
            self.steps[self.current_step_index]["completed"] = True
            if reason:
                self.steps[self.current_step_index]["failure_reason"] = reason

    def is_complete(self) -> bool:
        return all(step.get("completed", False) for step in self.steps)

    def get_completed_count(self) -> int:
        return sum(1 for step in self.steps if step.get("completed", False))


class ParkingPlanner:

    @staticmethod
    def create_scan_plan() -> Plan:
        steps = [
            {
                "action": "scan_spots",
                "params": {},
                "status": "pending",  # "pending", "in_progress", "completed", "failed"
                "completed": False,
            },
            {
                "action": "wait_user_input",
                "params": {},
                "status": "pending",  # "pending", "in_progress", "completed", "failed"
                "completed": False,
            },
        ]

        return Plan(steps)

    @staticmethod
    def create_parking_plan(target_spot_id: str) -> Plan:
        steps = [
            {
                "action": "find_spot_qr",
                "params": {"target_spot_id": target_spot_id},
                "status": "pending",  # "pending", "in_progress", "completed", "failed"
                "completed": False,
            },
            {
                "action": "reverse_entry",
                "params": {"target_spot_id": target_spot_id},
                "status": "pending",  # "pending", "in_progress", "completed", "failed"
                "completed": False,
            },
            {
                "action": "straighten",
                "params": {"target_spot_id": target_spot_id},
                "status": "pending",  # "pending", "in_progress", "completed", "failed"
                "completed": False,
            },
            {
                "action": "final_adjustment",
                "params": {"target_spot_id": target_spot_id},
                "status": "pending",  # "pending", "in_progress", "completed", "failed"
                "completed": False,
            },
        ]

        return Plan(steps)

    @staticmethod
    def replan(
        current_plan: Optional[Plan], current_state: dict[str, Any], reason: str = ""
    ) -> Plan:
        target_spot = current_state.get("target_spot")

        if reason == "obstacle_detected":
            # If an obstacle is detected, we may want to re-scan or wait for user input
            if target_spot:
                steps = [
                    {
                        "action": "scan_spots",
                        "params": {},
                        "status": "pending",  # "pending", "in_progress", "completed", "failed"
                        "completed": False,
                    },
                    {
                        "action": "find_spot_qr",
                        "params": {"target_spot_id": target_spot.id},
                        "status": "pending",  # "pending", "in_progress", "completed", "failed"
                        "completed": False,
                    },
                    {
                        "action": "align_with_spot",
                        "params": {"target_spot_id": target_spot.id},
                        "status": "pending",  # "pending", "in_progress", "completed", "failed"
                        "completed": False,
                    },
                    {
                        "action": "reverse_entry",
                        "params": {"target_spot_id": target_spot.id},
                        "status": "pending",  # "pending", "in_progress", "completed", "failed"
                        "completed": False,
                    },
                    {
                        "action": "straighten",
                        "params": {"target_spot_id": target_spot.id},
                        "status": "pending",  # "pending", "in_progress", "completed", "failed"
                        "completed": False,
                    },
                    {
                        "action": "final_adjustment",
                        "params": {"target_spot_id": target_spot.id},
                        "status": "pending",  # "pending", "in_progress", "completed", "failed"
                        "completed": False,
                    },
                ]
                return Plan(steps)

            # If no target spot, create a scan plan
            elif reason == "no_target_spot":
                return ParkingPlanner.create_scan_plan()

            elif reason == "execution_deviation":
                if current_plan and target_spot:
                    # Resume from the next incomplete step
                    completed_count = current_plan.get_completed_count()
                    new_plan = ParkingPlanner.create_parking_plan(target_spot.id)

                    for i in range(completed_count):
                        new_plan.mark_step_completed(i)

                    return new_plan

            if target_spot:
                return ParkingPlanner.create_parking_plan(target_spot.id)

        return ParkingPlanner.create_scan_plan()
