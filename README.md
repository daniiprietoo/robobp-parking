# Robobo Autonomous Parking System
An autonomous parking system for the Robobo robot

## Requirements

- Python 3.8+
- Robobo robot (physical or simulated RoboboSIM)
- `robobopy` library

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd final_project
   ```

2. Create and activate a conda environment (recommended):

   ```bash
   conda create -n robobo python=3.11
   conda activate robobo
   ```

3. Install the robobopy library:

   ```bash
   pip install robobopy
   ```

## Configuration

Edit `utils/config.py` to adjust robot parameters:

```python
# Movement speeds (0-100)
SPEED_SLOW = 5
SPEED_MEDIUM = 7
SPEED_NORMAL = 10
SPEED_FAST = 14

# Timing (seconds)
SPEECH_WAIT_TIME = 2
LOOP_DELAY = 0.1
REVERSE_DURATION = 4
STRAIGHTEN_DURATION = 2
TURNING_TIME = 7.3

# Camera positions (degrees)
PAN_LEFT = -90
PAN_RIGHT = 90
TILT_CENTER = 90

# Distance thresholds
TARGET_DISTANCE_TO_PILLAR = 60
QR_CENTER_TOLERANCE = 30
```

## Running the Project

### With Robobo Simulator

1. Start the Robobo simulator

2. Place map.json in the simulator's working directory.

3. Open the map in the simulator.

4. Run the main script:

   ```bash
   python main.py
    ```


10.20.27.237
