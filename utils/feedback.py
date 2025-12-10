from utils.planner import Plan
from utils.state import Spot
from robobopy.Robobo import Robobo


def display_parking_spots(spots: list[Spot]):
    """Display the list of detected parking spots."""
    if not spots:
        print("\n" + "=" * 60)
        print("  No parking spots detected yet.")
        print("=" * 60 + "\n")
        return

    print("\n" + "=" * 60)
    print("  AVAILABLE Parking Spots:")
    print("=" * 60 + "\n")
    print(f"{'ID':<8} {'Status':<12}")
    print("-" * 60)
    for spot in spots:
        status = "OCCUPIED" if spot.occupied else "FREE"
        status_symbol = "🚗" if spot.occupied else "✅"
        print(f"{spot.id:<8} {status_symbol} {status:<10}")

    print("=" * 60 + "\n")


def announce_parking_spots(robot: Robobo, spots: list[Spot]):
    """Announce the detected parking spots via text-to-speech."""
    if not spots:
        robot.sayText("No parking spots detected yet.")
        return

    free_spots = [spot for spot in spots if not spot.occupied]

    if not free_spots:
        robot.sayText("All detected parking spots are occupied.")
        return

    announcement = "Available parking spots are: "
    announcement += ", ".join(str(spot.id) for spot in free_spots)
    robot.sayText(announcement)


def prompt_for_parking_spot(robot: Robobo, spots: list[Spot]) -> str:
    """Prompt the user to select a parking spot via text-to-speech."""
    if not spots:
        robot.sayText("No spots available.")
        return ""

    free_spots = [spot for spot in spots if not spot.occupied]

    if not free_spots:
        robot.sayText("All detected parking spots are occupied.")
        return ""

    print("Please select a parking spot from the available options:")
    for spot in free_spots:
        print(f" - Spot ID: {spot.id}")

    try:
        user_input = input("Enter the parking spot ID to park: ").strip()
        return user_input
    except EOFError:
        print("No input available.")
        return "q"


def display_plan_progress(plan: Plan, current_step_index: int = 0):
    """Display the current progress of the parking plan."""
    print("\n" + "=" * 60)
    print("  PARKING PLAN PROGRESS:")
    print("=" * 60 + "\n")

    for i, step in enumerate(plan.steps):
        status = step.get("status", "pending")
        marker = ">>" if i == current_step_index else "  "
        print(f"{marker} Step {i + 1}: {step['action']} - Status: {status}")

    print("\n" + "=" * 60 + "\n")
