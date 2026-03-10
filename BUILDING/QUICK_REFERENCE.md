# Building Navigation MCP Server - Quick Reference

## 🚀 Start Server

```bash
cd building_dev/BUILDING
python mcp_server.py
```

## 📞 MCP Tools (8 Tools)

### Load Buildings

```python
# 4-story with blue lines
load_4story_building()

# Single-story with vision
load_single_story(scene_name='FloorPlan301')
```

### Create & Move Agent

```python
# Spawn agent
create_agent()

# Move with custom increments
move_agent(dx=1.0, dy=0.0, dz=0.0)  # Right 1m
move_agent(dx=0.0, dy=0.0, dz=0.5)  # Forward 0.5m
move_agent(dx=0.0, dy=0.5, dz=0.3)  # Up stairs (4-story)
```

### Query State

```python
# Get position
get_agent_position()

# Get blue line path (4-story)
get_blue_line_path()
```

### Vision (Single-Story)

```python
# See what you're seeing
get_first_person_view(save_path="view.png")

# See what's around you
get_nearby_objects(radius=2.0)
```

## 🎯 Quick Examples

### 4-Story Navigation

```python
from mcp_server import BuildingNavigationServer

s = BuildingNavigationServer()
s.load_4story_building()
s.create_agent()

# Explore floor
s.move_agent(dx=1.0, dz=0.0)

# To stairs (blue line)
for _ in range(5):
    s.move_agent(dx=1.0, dz=0.2)

# Climb stairs
for _ in range(6):
    s.move_agent(dy=0.5, dz=0.3)
```

### Single-Story with Vision

```python
s = BuildingNavigationServer()
s.load_single_story()
s.create_agent()

# Walk and see
s.move_agent(dz=0.5)
s.get_first_person_view("step1.png")
s.get_nearby_objects(radius=2.0)
```

## 📐 Coordinate System

- **dx**: Left (-) / Right (+)
- **dy**: Down (-) / Up (+) - Vertical
- **dz**: Back (-) / Forward (+)

## 🎮 Movement Sizes

- Tiny: `0.1m`
- Small: `0.25m`
- Medium: `0.5m`
- Large: `1.0m`
- Jump: `2.0m`

## 🏢 Building Types

**4-Story:**
- Blue line paths
- Floor detection
- Stairwell (12 steps/flight)
- Boundary checking

**Single-Story:**
- First-person view
- Object detection
- Visibility checking
- AI2Thor scenes (1-430)

## 💡 Pro Tips

1. **Follow blue lines** in 4-story for optimal navigation
2. **Check nearby objects** before moving in single-story
3. **Save views** at each step to visualize journey
4. **Use small increments** (0.1-0.25m) for precision
5. **Try different scenes** (FloorPlan1-430)

## 🐛 Quick Fixes

**No building found:**
```bash
cd ../building/test && python create_4story_advanced.py
```

**Movement blocked:**
- Check bounds with `get_agent_position()`
- Use smaller increments

**AI2Thor error:**
- Try different scene
- Reduce quality in mcp_server.py

## 📚 Full Docs

See [README.md](README.md) for complete documentation.

---

**Ready to navigate!** 🎉
