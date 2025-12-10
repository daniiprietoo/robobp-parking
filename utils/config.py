"""
Constants and configuration values for the parking robot project.
Centralized location for all magic numbers and settings.
"""

# =============================================================================
# MOVEMENT SPEEDS
# =============================================================================
SPEED_SLOW = 5
SPEED_MEDIUM = 7
SPEED_NORMAL = 10
SPEED_FAST = 12
SPEED_REVERSE_SLOW = -5
SPEED_REVERSE_FAST = -12

# =============================================================================
# TIMING (in seconds)
# =============================================================================
SPEECH_WAIT_TIME = 2
ACTION_WAIT_TIME = 0.05
LOOP_DELAY = 0.01
REVERSE_DURATION = 4
STRAIGHTEN_DURATION = 2
FINAL_ADJUST_DURATION = 1
ROBOT_WAIT_SHORT = 2
ROBOT_WAIT_LONG = 3

# =============================================================================
# CAMERA POSITIONS (Pan/Tilt in degrees)
# =============================================================================
PAN_CENTER = 0
PAN_LEFT = -90
PAN_RIGHT = 90
TILT_CENTER = 90
TILT_UP = 109
TILT_DOWN = 70

# =============================================================================
# SENSOR THRESHOLDS
# =============================================================================
# IR Sensor distances
IR_OBSTACLE_THRESHOLD = 20
IR_CLOSE_THRESHOLD = 50
IR_FAR_THRESHOLD = 100

# Distance thresholds (in cm or sensor units)
TARGET_DISTANCE_TO_PILLAR = 60
MIN_ROTONDA_DISTANCE = 70
QR_CENTER_TOLERANCE = 20
PARKING_SPOT_MIN_WIDTH = 30

# =============================================================================
# QR CODE DETECTION
# =============================================================================
QR_DETECTION_CONFIDENCE = 0.8
QR_MIN_SIZE = 50
QR_MAX_SIZE = 500

# =============================================================================
# PARKING ACTIONS
# =============================================================================
PARKING_ACTIONS = ["reverse_entry", "final_adjustment", "straighten"]

# =============================================================================
# STATE VALUES
# =============================================================================
# Parking states
STATE_IDLE = "idle"
STATE_SEARCHING = "searching"
STATE_PLANNING = "planning"
STATE_EXECUTING = "executing"
STATE_COMPLETED = "completed"
STATE_FAILED = "failed"
STATE_WAITING_FOR_INPUT = "waiting_for_input"

# Action statuses
ACTION_STATUS_PENDING = "pending"
ACTION_STATUS_EXECUTING = "executing"
ACTION_STATUS_COMPLETED = "completed"
ACTION_STATUS_FAILED = "failed"

# =============================================================================
# DEFAULT VALUES
# =============================================================================
DEFAULT_SIDE = "left"
DEFAULT_SPOT_INDEX = 0

# =============================================================================
# TIMEOUTS (in seconds)
# =============================================================================
ACTION_TIMEOUT = 180
CONNECTION_TIMEOUT = 30
SCAN_TIMEOUT = 60

# =============================================================================
# ROBOT PHYSICAL CONSTANTS
# =============================================================================
WHEEL_BASE_CM = 10  # Distance between wheels
ROBOT_LENGTH_CM = 15
ROBOT_WIDTH_CM = 12

# =============================================================================
# DEBUG/LOGGING
# =============================================================================
DEBUG_MODE = True
VERBOSE_LOGGING = True
