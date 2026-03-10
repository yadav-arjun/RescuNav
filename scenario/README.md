# Scenario Simulations

This folder contains simulation scenarios for building evacuation and security analysis.

## Structure

- **`fire/`**: Fire expansion simulations
- **`attacker/`**: Attacker search simulations

## Fire Simulations

### Single-Story Building (First-Person View)

**File**: `fire/fire_single_story.py`

Simulates fire expansion through a single-story building from first-person perspective.

**Features:**
- Fire starts at building center (or specified position)
- Fire expands outward in all directions
- Red-colored fire visualization
- First-person view captures saved to `fire_views/` directory
- Uses AI2Thor scene (FloorPlan301)

**Usage:**
```bash
cd scenario/fire
python fire_single_story.py
```

### 4-Story Building (Third-Person View)

**File**: `fire/fire_4story.py`

Simulates fire expansion through a 4-story building from third-person perspective.

**Features:**
- Fire starts on ground floor (or specified floor/position)
- Fire expands horizontally and vertically through floors
- Red sphere meshes represent fire points
- Real-time 3D visualization with PyVista
- Fire can spread between floors

**Usage:**
```bash
cd scenario/fire
python fire_4story.py
```

**Prerequisites:**
- Requires a 4-story building file (`.vtk` format)
- Will search for `ai2thor_4story_building.vtk` or `unified_4story_building.vtk`

## Attacker Simulations

### Single-Story Building (First-Person View)

**File**: `attacker/attacker_single_story.py`

Simulates an attacker searching for agents in a single-story building from first-person perspective.

**Features:**
- Systematic grid-based search pattern
- Small, controlled movement steps (0.25m)
- Stays within building walls
- Detects agents within 3.0m radius
- Reports findings to terminal
- First-person view during search

**Usage:**
```bash
cd scenario/attacker
python attacker_single_story.py
```

**Output:**
- If agents found: Reports agent locations and types
- If no agents found: Reports "No agents found in building"

### 4-Story Building (Third-Person View)

**File**: `attacker/attacker_4story.py`

Simulates an attacker searching for agents in a 4-story building from third-person perspective.

**Features:**
- Systematic search across all floors
- Small, controlled movement steps (0.3m)
- Stays within building walls and floor bounds
- Zigzag search pattern on each floor
- Real-time 3D visualization with attacker marker (dark red)
- Detects agents within 4.0m radius
- Reports findings to terminal

**Usage:**
```bash
cd scenario/attacker
python attacker_4story.py
```

**Prerequisites:**
- Requires a 4-story building file (`.vtk` format)
- Will search for `ai2thor_4story_building.vtk` or `unified_4story_building.vtk`

**Output:**
- If agents found: Reports agent locations, floors, and types
- If no agents found: Reports "No agents found in building"

## Framework Files

### Fire Simulation Framework

**File**: `fire/fire_simulation_framework.py`

Contains:
- `FireSimulationSingleStory`: First-person fire simulation
- `FireSimulationMultiStory`: Third-person fire simulation

### Attacker Simulation Framework

**File**: `attacker/attacker_simulation_framework.py`

Contains:
- `AttackerSimulationSingleStory`: First-person attacker search
- `AttackerSimulationMultiStory`: Third-person attacker search

## Movement Characteristics

All simulations use **small, controlled movements**:
- Single-story: 0.25m steps
- Multi-story: 0.3m steps
- Movements stay within building walls and floor bounds
- Smooth, realistic walking simulation

## View Modes

- **Single-Story Buildings**: Always **first-person view**
- **4-Story Buildings**: Always **third-person view**

## Dependencies

- `numpy`: Numerical operations
- `pyvista`: 3D visualization (multi-story)
- `ai2thor`: Single-story scenes and first-person view
- `opencv-python`: Image processing for view capture
- Framework classes from `BUILDING/agent_visualization_framework.py`

## Notes

- Fire simulations create red-colored surfaces/spheres that expand through the building
- Attacker simulations search systematically but currently find no agents (structure ready for when agents are added)
- All movements respect building geometry and stay within walls
- Simulations can be interrupted with Ctrl+C

