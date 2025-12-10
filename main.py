from robobopy.Robobo import Robobo

from behaviors.find_qr import FindQR
from behaviors.parking_beh import Parking
from behaviors.scan_spots import ScanSpots

from utils.planner import ParkingPlanner
from utils.executor import Executor
from utils.state import StateManager
from utils.feedback import (
    announce_parking_spots,
    display_parking_spots,
    prompt_for_parking_spot,
    display_plan_progress,
)
import time


def main():
    # Create a Robobo object and connect to the robot
    robobo = Robobo("localhost")
    robobo.connect()

    # Dictionary to share parameters between behaviors
    # The "stop" flag will indicate when the task is complete
    params = StateManager()
    planner = ParkingPlanner()
    executor = Executor(robobo, params)

    # Create behavior instances
    # Each behavior is a thread with specific logic
    scan_spots_behaviour = ScanSpots(robobo, [], params)
    find_qr = FindQR(robobo, [scan_spots_behaviour], params)
    # Rotonda detection is now integrated into FindQR behavior
    parking_behaviour = Parking(robobo, [scan_spots_behaviour, find_qr], params)

    threads = [find_qr, parking_behaviour, scan_spots_behaviour]

    # Start all behaviors (threads)
    for thread in threads:
        thread.start()

    current_plan = None

    try:
        params.set("parking_state", "scanning")

        while not params.get("stop", False):
            parking_state = params.get("parking_state", "scanning")

            if executor.should_replan(current_plan):
                replan_reason = params.get("replan_reason", None)
                print(f"[Main] Replanning due to: {replan_reason}")

                params.set("replan_needed", False)
                params.set("replan_reason", None)

                params.set("parking_state", "planning")

                current_plan = planner.replan(current_plan, params, replan_reason)
                params.set("current_plan", current_plan)
                params.set("current_step_index", 0)

                print("[Main] New plan created.")

            if current_plan is None:
                if parking_state == "scanning":
                    current_plan = planner.create_scan_plan()
                    print("[Main] Created scan plan.")
                    params.set("parking_state", "scanning")
                    params.set("current_plan", current_plan)
                    params.set("current_step_index", 0)

            if parking_state == "waiting_for_input" or ():
                print("[Main] Waiting for user to select parking spot...")
                spots = params.get_detected_spots()

                if current_plan and params.get("current_action") != "wait_user_input":
                    params.set("current_action_status", "waiting_for_input")

                if spots:
                    display_parking_spots(spots)
                    announce_parking_spots(robobo, spots)
                    if current_plan is not None:
                        for i, step in enumerate(current_plan.steps):
                            if step.get("action") == "wait_user_input":
                                current_plan.steps[i]["status"] = "in_progress"
                    print(
                        f"[Main] About to prompt user. parking_state={parking_state}, current_action={params.get('current_action')}, current_action_status={params.get('current_action_status')}"
                    )
                    user_choice = prompt_for_parking_spot(robobo, spots)

                    if user_choice and user_choice.lower() == "q":
                        print("[Main] User opted to quit.")
                        params.set("stop", True)
                        break

                    if user_choice:
                        try:
                            spot_id = user_choice.strip()

                            selected_spot = next(
                                (
                                    spot
                                    for spot in spots
                                    if spot.id == spot_id and not spot.occupied
                                ),
                                None,
                            )

                            if selected_spot:
                                params.set("target_spot", spot_id)
                                params.set("current_action_status", "completed")
                                params.set("parking_state", "planning")
                                params.set("current_action", None)
                                params.set("current_action_params", None)
                                params.set("parking_state", "planning")
                                print(
                                    f"[Main] User selected spot {spot_id} for parking."
                                )
                            else:
                                robobo.sayText(
                                    "Invalid selection or spot is occupied. Please try again."
                                )
                                time.sleep(2)
                                continue
                        except Exception as e:
                            print(f"[Main] Error processing user input: {e}")
                            robobo.sayText(
                                "Error processing your selection. Please try again."
                            )
                            time.sleep(2)
                            continue

            # Create parking after user input
            if params.get("target_spot") and parking_state == "planning":
                target_spot_id = params.get("target_spot")
                current_plan = planner.create_parking_plan(target_spot_id)
                params.set("current_plan", current_plan)
                params.set("current_step_index", 0)
                params.set("parking_state", "executing")
                params.set("current_action", None)
                params.set("current_action_params", None)
                print(f"[Main] Created parking plan for spot {target_spot_id}.")
                if current_plan is not None:
                    print(
                        "[Main] Parking plan steps: ",
                        [step["action"] for step in current_plan.steps],
                    )
            if (
                current_plan
                and not current_plan.is_complete()
                and parking_state in ["scanning", "executing"]
            ):
                if parking_state == "scanning":
                    params.set("parking_state", "executing")

                success = executor.execute_plan(current_plan)
                display_plan_progress(
                    current_plan, current_step_index=params.get("current_step_index")
                )
                if not success:
                    if params.get("replan_needed"):
                        print("[Main] Plan execution failed, replanning...")
                        continue
                    else:
                        print(
                            "[Main] Plan execution failed, but no replanning requested."
                        )
                        params.set("stop", True)
                        break

            if (
                current_plan
                and not current_plan.is_complete()
                and parking_state in ["scanning", "executing"]
            ):
                executor.execute_plan(current_plan)

            if current_plan and current_plan.is_complete():
                plan_actions = [step["action"] for step in current_plan.steps]
                target_spot = params.get("target_spot")
                if "wait_user_input" in plan_actions:
                    if not target_spot:
                        print(
                            "[Main] Scanning complete, returning to waiting for user input."
                        )
                        params.set("parking_state", "waiting_for_input")
                        params.set("current_action", "wait_user_input")
                    else:
                        print(
                            "[Main] Scanning complete and spot selected, parking now."
                        )
                        params.set("parking_state", "planning")
                else:
                    if target_spot:
                        print("[Main] Parking maneuver complete.")
                        params.set("parking_state", "done")
                        params.set("stop", True)
                current_plan = None
        time.sleep(0.1)

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, stopping all behaviors...")
        params.set("stop", True)

    finally:
        print("Stopping all behaviors...")
        params.set("stop", True)
        # Wait for all threads to finish
        # This ensures that all behaviors complete their cleanup before exiting
        for thread in threads:
            thread.join()

    robobo.sayText("Mission complete")
    time.sleep(2)  # Wait for the message to be spoken
    # Disconnect the robot once the mission is complete
    robobo.disconnect()


if __name__ == "__main__":
    main()
