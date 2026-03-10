# Building Navigation MCP Server

**Model Context Protocol (MCP) Server for 4-Story and Single-Story Building Navigation**

---

## Quick Start

### 1. Run MCP Server

```bash
cd building_dev/BUILDING
python mcp_server.py
```

### 2. Run Example Client

```bash
python example_client.py
```

---

## What This MCP Server Does

This MCP server provides **two separate building navigation systems**:

### 🏢 4-Story Building
- Load unified 4-story building mesh
- Navigate with **blue line paths** showing optimal routes between floors
- Move agent with custom X, Y, Z increments
- Check if on blue line path
- Track which floor agent is on

### 🏠 Single-Story Building
- Load AI2Thor single-story scenes (FloorPlan301-330)
- Navigate with custom X, Y, Z increments
- **See what you're walking through** via first-person view
- Get nearby objects within radius
- Detect visible objects from current position
- Save first-person view screenshots

---

## MCP Tools Available

### Building Management

#### `load_4story_building`
Load a 4-story building with blue line navigation paths.

**Parameters:**
- `building_file` (optional): Path to VTK file (auto-searches if not provided)

**Returns:**
- Building statistics (vertices, faces, floors)
- Agent spawn position
- Blue line waypoint count

**Example:**
```python
server.load_4story_building()
# or
server.load_4story_building(building_file="path/to/building.vtk")
```

#### `load_single_story`
Load AI2Thor single-story scene with first-person view capability.

**Parameters:**
- `scene_name` (optional): Scene name (default: 'FloorPlan301')

**Returns:**
- Scene information
- Reachable positions count
- Object types in scene
- Agent spawn position

**Example:**
```python
server.load_single_story(scene_name='FloorPlan301')
```

---

### Agent Control

#### `create_agent`
Create a navigable agent at specified position.

**Parameters:**
- `x`, `y`, `z` (optional): Initial position (uses spawn point if not specified)

**Returns:**
- Agent position
- Current floor (for 4-story)

**Example:**
```python
server.create_agent()
# or
server.create_agent(x=0.0, y=0.5, z=0.0)
```

#### `move_agent`
Move agent by specified increments - **custom dx, dy, dz**

**Parameters:**
- `dx`: X-axis movement increment (default: 0.0)
- `dy`: Y-axis movement increment (default: 0.0) - vertical for 4-story
- `dz`: Z-axis movement increment (default: 0.0)

**Returns:**
- New position
- Movement deltas
- Blue line status (4-story) OR visible objects (single-story)

**Example:**
```python
# Move right 1m
server.move_agent(dx=1.0, dy=0.0, dz=0.0)

# Move forward 0.5m
server.move_agent(dx=0.0, dy=0.0, dz=0.5)

# Go up stairs (4-story)
server.move_agent(dx=0.0, dy=0.5, dz=0.3)

# Small step forward
server.move_agent(dx=0.0, dy=0.0, dz=0.1)

# Large jump
server.move_agent(dx=2.0, dy=0.0, dz=1.0)
```

---

### Query Tools

#### `get_agent_position`
Get current agent position and state.

**Returns:** JSON with:
- Position [x, y, z]
- Building type (4-story or single-story)
- Floor number (4-story)
- Blue line status (4-story)

**Example:**
```python
server.get_agent_position()
```

#### `get_blue_line_path`
Get the blue line navigation path (4-story only).

**Returns:**
- Total waypoints
- Path data

**Example:**
```python
server.get_blue_line_path()
```

---

### Single-Story Vision Tools (See What You're Walking Through)

#### `get_first_person_view`
**Capture what the agent is seeing** from current position.

**Parameters:**
- `save_path` (optional): Where to save image (default: 'first_person_view.png')

**Returns:**
- Image path
- Agent position & rotation
- List of visible objects with distances

**Example:**
```python
server.get_first_person_view(save_path="my_view.png")
```

**Output:**
```
First-Person View Saved: my_view.png
Position: [1.5, 0.9, 2.3]
Rotation: {'x': 0, 'y': 90, 'z': 0}
Visible objects: 8
  1. CounterTop - 1.23m away
  2. Microwave - 1.45m away
  3. CoffeeMachine - 1.67m away
  ...
```

#### `get_nearby_objects`
**See what you're walking through** - get objects near agent.

**Parameters:**
- `radius` (optional): Search radius in meters (default: 3.0)

**Returns:**
- Objects within radius
- Distance to each object
- Visibility status

**Example:**
```python
server.get_nearby_objects(radius=2.0)
```

**Output:**
```
Objects within 2.0m
Found: 5 objects

👁️ 1. CounterTop - 0.45m
👁️ 2. Sink - 0.78m
   3. Cabinet - 1.23m
👁️ 4. Fridge - 1.56m
   5. Toaster - 1.89m
```

(👁️ = currently visible)

---

## Usage Examples

### Example 1: 4-Story Building with Blue Lines

```python
from mcp_server import BuildingNavigationServer

server = BuildingNavigationServer()

# Load building
server.load_4story_building()

# Create agent
server.create_agent()

# Move around floor 1
server.move_agent(dx=1.0, dz=0.0)  # Move right
server.move_agent(dx=0.0, dz=1.0)  # Move forward

# Check position
server.get_agent_position()

# Move towards stairwell (blue line)
for i in range(5):
    server.move_agent(dx=1.0, dz=0.2)  # Towards stairs

# Climb stairs
for i in range(6):
    server.move_agent(dx=0.0, dy=0.5, dz=0.3)  # Up stairs

# Now on floor 2!
server.get_agent_position()
```

### Example 2: Single-Story - See What You're Walking Through

```python
from mcp_server import BuildingNavigationServer

server = BuildingNavigationServer()

# Load scene
server.load_single_story(scene_name='FloorPlan301')

# Create agent
server.create_agent()

# Capture initial view
server.get_first_person_view(save_path="start.png")

# See what's nearby
server.get_nearby_objects(radius=3.0)

# Walk forward and see changes
server.move_agent(dx=0.0, dz=0.5)
server.get_first_person_view(save_path="step1.png")
server.get_nearby_objects(radius=2.0)

# Continue exploring
server.move_agent(dx=0.5, dz=0.0)  # Move right
server.get_first_person_view(save_path="step2.png")
```

### Example 3: Custom Movement Increments

```python
server = BuildingNavigationServer()
server.load_single_story()
server.create_agent()

# Try different step sizes
increments = [0.1, 0.25, 0.5, 1.0, 2.0]

for inc in increments:
    print(f"\nMoving {inc}m forward:")
    result = server.move_agent(dx=0.0, dz=inc)
    print(result['content'][0]['text'])

    # See what's around
    server.get_nearby_objects(radius=1.5)
```

---

## File Structure

```
building_dev/BUILDING/
├── mcp_server.py           ← Main MCP server
├── mcp_config.json         ← MCP server configuration
├── example_client.py       ← Usage examples
├── README.md               ← This file
└── DOCUMENTATION.md        ← Complete guide
```

---

## MCP Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "building-navigation": {
      "command": "python",
      "args": ["building_dev/BUILDING/mcp_server.py"]
    }
  }
}
```

---

## Key Features

### 4-Story Building
✓ Blue line navigation paths between floors
✓ Stairwell detection (12 steps per flight)
✓ Floor tracking (auto-detect which floor)
✓ Path distance checking
✓ Boundary enforcement (can't walk outside)
✓ Custom movement increments (dx, dy, dz)

### Single-Story Building
✓ First-person view capture ("what am I seeing?")
✓ Nearby object detection ("what's around me?")
✓ Distance to objects
✓ Visibility status
✓ AI2Thor scene integration
✓ Custom movement increments (dx, dy, dz)

---

## Coordinate System

**AI2Thor & PyVista:**
- **X-axis**: Left (-) to Right (+)
- **Y-axis**: Down (-) to Up (+) - **Vertical**
- **Z-axis**: Back (-) to Forward (+)

**Movement Examples:**
- `dx = +1.0` → Move right
- `dx = -1.0` → Move left
- `dz = +1.0` → Move forward
- `dz = -1.0` → Move backward
- `dy = +1.0` → Move up (4-story only)

---

## AI2Thor Scenes Available

**Kitchens:** FloorPlan1-30
**Living Rooms:** FloorPlan201-230
**Bedrooms:** FloorPlan301-330
**Bathrooms:** FloorPlan401-430

**Example:**
```python
server.load_single_story(scene_name='FloorPlan220')  # Living room
```

---

## Requirements

```bash
pip install ai2thor pyvista numpy opencv-python
```

---

## Next Steps

1. **Run examples:** `python example_client.py`
2. **Read full docs:** [DOCUMENTATION.md](DOCUMENTATION.md)
3. **Integrate with MCP client:** Use tools in your application
4. **Customize:** Modify movement increments, add new tools

---

## Troubleshooting

### "No building file found"
```bash
cd ../building/test
python create_4story_advanced.py
```

### AI2Thor won't initialize
- Check display settings
- Try different scene (FloorPlan1-430)
- Reduce quality in `mcp_server.py`

### Movement blocked
- Check building bounds
- Verify position is valid
- For single-story: AI2Thor may block unreachable positions

---

## MCP Tools Summary

| Tool | 4-Story | Single-Story | Purpose |
|------|---------|--------------|---------|
| `load_4story_building` | ✓ | - | Load 4-story mesh |
| `load_single_story` | - | ✓ | Load AI2Thor scene |
| `create_agent` | ✓ | ✓ | Spawn agent |
| `move_agent(dx,dy,dz)` | ✓ | ✓ | Move with increments |
| `get_agent_position` | ✓ | ✓ | Get current state |
| `get_blue_line_path` | ✓ | - | Get nav path |
| `get_first_person_view` | - | ✓ | **See what you see** |
| `get_nearby_objects` | - | ✓ | **See what's around** |

---

**Ready to navigate!** 🏢🏠

For complete documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)
