# AGENTS.md

This file contains guidelines and commands for agentic coding agents working on this Robobo autonomous parking system.

## Project Overview

This is a Python-based autonomous parking system for the Robobo robot that uses computer vision (QR code detection) and multi-threaded behaviors to navigate and park in designated spots.

**Key Technologies:**
- Python 3.8+ with type hints
- robobopy library for robot control
- Threading-based behavior architecture
- Computer vision for QR code detection

## Development Commands

### Running the Application
```bash
# Main autonomous parking system
python main.py

# Simple robot connection and movement test
python test.py

# Interactive parking maneuver testing tool
python parking_tester.py
```

### Testing
**No automated test framework detected.** Testing is done through:
- Manual testing with `test.py` (basic robot connectivity)
- Interactive testing with `parking_tester.py`
- Real-world robot testing

### Code Quality
**No linting/formatting tools configured.** Recommended to add:
- `black` for code formatting
- `flake8` or `pylint` for linting
- `mypy` for type checking

## Code Style Guidelines

### Import Organization
```python
# Standard library imports first
import time
import threading
from dataclasses import dataclass
from typing import Optional

# Third-party imports second
from robobopy.Robobo import Robobo

# Local imports third - use absolute imports
from behaviors.behaviors import Behaviour
from utils.config import SPEED_NORMAL
from utils.state import StateManager
```

### Naming Conventions
- **Variables/Functions**: `snake_case` (e.g., `target_spot_id`, `take_control`)
- **Classes**: `CamelCase` (e.g., `Behaviour`, `StateManager`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `SPEED_NORMAL`, `LOOP_DELAY`)
- **Private members**: Prefix with underscore (e.g., `_is_moving`, `_lock`)

### Type Hints
- Use type hints consistently (Python 3.8+ style)
- Import from `typing` module for complex types
- Use `Optional[T]` for nullable values
- Use forward references for circular imports: `list["Behaviour"]`

### Class Structure
```python
class ClassName:
    """
    Brief description of the class purpose.
    
    Longer description if needed.
    """
    
    def __init__(self, param1: Type1, param2: Type2):
        self.param1 = param1
        self.param2 = param2
        self._private_var = None
    
    def public_method(self) -> ReturnType:
        """Method description."""
        pass
    
    def _private_method(self) -> None:
        """Private method description."""
        pass
```

### Error Handling
- Use try-except blocks for robot operations
- Include descriptive error messages with context
- Handle keyboard interrupts gracefully in main loops
- Use StateManager for error state communication

### Threading Guidelines
- All behaviors inherit from `Behaviour` (Thread subclass)
- Use `StateManager` for thread-safe state sharing
- Include `LOOP_DELAY` in behavior loops to reduce CPU usage
- Always check `params.get("stop", False)` in loops
- Use `suppress_others()` and `release_others()` for behavior control

### Configuration Management
- All constants go in `utils/config.py`
- Group related constants with comments
- Use descriptive names with units in comments
- Example: `SPEED_SLOW = 5  # Movement speed for slow operations`

### State Management
- Use `StateManager` for all shared state between threads
- Use thread-safe methods: `get()`, `set()`, `update()`
- Use dataclasses for structured data (e.g., `Spot` class)
- Include default values in `get()` calls

### Robot Control Patterns
- Always connect before using robot: `robobo.connect()`
- Use `robobo.wait(seconds)` for timing delays
- Stop motors before disconnect: `robobo.stopMotors()`
- Always disconnect: `robobo.disconnect()`
- Use speech feedback: `robobo.sayText("message")`

### Documentation
- Use docstrings for all classes and public methods
- Include parameter types and return values
- Add inline comments for complex logic
- Use print statements with context for debugging: `[ClassName] Description`

## Architecture Patterns

### Behavior-Based Architecture
- Each behavior is a separate thread
- Behaviors use `take_control()` to determine when to run
- Use suppression mechanism to prevent conflicts
- Main loop coordinates behavior execution

### Plan-Execute Pattern
- Generate plans using `ParkingPlanner`
- Execute plans using `Executor`
- Support replanning when needed
- Track plan progress with state management

### State Management
- Centralized state using `StateManager`
- Thread-safe operations with locks
- Structured data using dataclasses
- Clear state transitions (scanning → planning → executing)

## File Organization

```
behaviors/          # Robot behavior modules
├── behaviors.py    # Base behavior class
├── find_qr.py      # QR code detection
├── parking_beh.py # Parking maneuvers
└── scan_spots.py  # Spot scanning

utils/              # Utility modules
├── config.py       # Configuration constants
├── executor.py     # Plan execution
├── feedback.py     # User feedback
├── planner.py      # Plan generation
└── state.py        # State management
```

## Development Notes

- Robot IP address may need updating in test files
- The system supports both real robot and RoboboSIM simulator
- Camera positions are configurable via constants
- All timing values are in seconds
- Distance measurements are in robot units
- The system uses QR codes for spot identification

## Common Pitfalls

- Forgetting to check `stop` flag in loops
- Not using thread-safe state operations
- Missing `LOOP_DELAY` causing high CPU usage
- Not handling robot disconnection properly
- Hardcoding robot IP in multiple files