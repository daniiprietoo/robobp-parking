from utils.planner import Plan
from utils.state import StateManager
from robobopy.Robobo import Robobo
import time


class Executor:
    def __init__(self, robot: Robobo, state_manager: StateManager):
        self.robot = robot
        self.state_manager = state_manager

    def execute_plan(self, plan: Plan):
        if not plan or plan.is_complete():
            print("[Executor] No plan to execute or plan is already complete.")
            return

        self.state_manager.set("current_plan", plan)
        self.state_manager.set("current_step_index", 0)

        while not plan.is_complete():
            if self.should_replan(plan):
                return False

            current_step = plan.get_next_step()
            if current_step is None:
                break

            step_index = plan.current_step_index
            current_step["status"] = "in_progress"
            self.state_manager.set("current_step_index", step_index)

            print(f"[Executor] Executing step {step_index}: {current_step['action']}")

            success = self.execute_step(current_step, plan, step_index)

            if success == "waiting_for_input":
                print("[Executor] Waiting for user input to proceed.")
                return True  # Pause execution until user input is received
            if success:
                plan.mark_step_completed(step_index)
                print(f"[Executor] Step {step_index} completed successfully.")
            else:
                plan.mark_step_failed(step_index, reason="Step execution failed.")
                print(f"[Executor] Step {step_index} failed.")
                if self.should_replan_on_failure(current_step):
                    print("[Executor] Replanning due to step failure.")
                    return False

            time.sleep(0.1)

        print("[Executor] Plan execution complete.")
        return True

    def execute_step(self, step: dict, plan: Plan, step_index: int) -> bool:
        action = step.get("action")
        params = step.get("params", {})

        self.state_manager.set("current_action", action)
        self.state_manager.set("current_action_params", params)
        self.state_manager.set("current_action_status", "executing")

        timeout = 180

        start_time = time.time()

        if action == "wait_user_input":
            print(
                "[Executor] Entering wait_user_input step; returning to main for user input."
            )
            self.state_manager.set("current_action_status", "waiting_for_input")
            # Indicate overall parking state
            self.state_manager.set("parking_state", "waiting_for_input")
            return "waiting_for_input"

        while True:
            if time.time() - start_time > timeout:
                print(f"[Executor] Action '{action}' timed out.")
                return False

            status = self.state_manager.get("current_action_status")
            print(f"[Executor] DEBUG: action={action}, status={status}")  # TEMP

            if status == "completed":
                print(f"[Executor] Action '{action}' completed successfully.")
                return True
            elif status == "failed":
                return False
            elif self.state_manager.get("stop", False):
                print(f"[Executor] Action '{action}' was stopped.")
                return False
            elif self.should_replan(plan):
                print(f"[Executor] Replanning triggered during action '{action}'.")
                return False

            time.sleep(0.1)

    def should_replan(self, plan: Plan) -> bool:
        return self.state_manager.get("replan_needed", False)

    def should_replan_on_failure(self, step: dict) -> bool:

        action = step.get("action")
        critical_actions = ["find_spot_qr", "approach_spot", "align_with_spot"]

        if action in critical_actions:
            return True

        return False
