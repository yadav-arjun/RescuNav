# 🏢 4-Story Building Navigation System

## 🚀 Quick Start in 3 Steps

### Step 1: Install
```bash
pip install ai2thor pyvista numpy trimesh
```

### Step 2: Run Main Simulation
```bash
python building_navigation_sim.py
```

### Step 3: Watch!
- Choose option `[2]` for normal speed
- Watch agent navigate through all 4 floors
- See boundary enforcement in action
- Observe realistic floor exploration

---

## 📁 What's in This Folder?

```
building/
├── 📄 START_HERE.md               ← You are here!
├── 📄 README.md                   ← Quick reference
├── 📚 BUILDING_DOCUMENTATION.md   ← Complete guide
│
├── 🎯 building_navigation_sim.py  ← MAIN SIMULATION FILE
│
└── 📂 test/                       ← Testing & generation scripts
    ├── create_4story_advanced.py  ← Generate buildings
    ├── test_*.py                  ← Various tests
    └── run_all_tests.py           ← Test runner
```

---

## 🎯 Main Simulation File

**`building_navigation_sim.py`** is your primary file.

### What It Does

✅ Loads a 4-story building
✅ Creates an agent that navigates through all floors
✅ Enforces boundaries (agent stays inside building)
✅ Shows realistic floor exploration
✅ Demonstrates stair climbing
✅ Displays real-time progress

### How to Run

```bash
python building_navigation_sim.py
```

Select option:
- `[1]` Fast (0.1s per move) - Quick demo
- `[2]` Normal (0.3s per move) - **Recommended**
- `[3]` Slow (0.8s per move) - Detailed view
- `[0]` Skip animation

---

## 🏗️ Need a Building First?

If you get "No building file found", generate one:

```bash
cd test
python create_4story_advanced.py
cd ..
python building_navigation_sim.py
```

---

## 📖 Documentation

### Quick Reference
→ [README.md](README.md) - Fast overview, key commands

### Complete Guide
→ [BUILDING_DOCUMENTATION.md](BUILDING_DOCUMENTATION.md) - Everything you need to know

**Includes:**
- Installation details
- System architecture
- All features explained
- Customization guide
- Troubleshooting
- Bug fixes (v2.0)
- Advanced topics

---

## 🎮 What You'll See

When you run the main simulation:

### Color Coding
- 🔴 **Red agent** = Free movement on floor
- 🔵 **Blue agent** = Following path to stairs ("blue line")
- 🟠 **Orange agent** = Climbing stairs

### Display Elements
- Semi-transparent building (see inside)
- Green box = Safe navigation area (1m from walls)
- Blue path line = Complete route through building
- Status text = Current floor, position, progress

### Movement Pattern
1. **Floor 1**: Agent explores randomly within bounds
2. **Blue line**: Agent walks to stairwell entry
3. **Stairs**: Agent climbs 12 steps to Floor 2
4. **Floor 2**: Agent explores... repeat for all 4 floors
5. **Descend**: Agent comes back down via stairs
6. **Complete**: Final report shows all verifications ✓

---

## ✨ Key Features (v2.0)

### ✓ Boundary Enforcement
- Agent **NEVER** walks outside building
- 1-meter wall margin enforced
- All waypoints verified within safe bounds

### ✓ Free Floor Exploration
- Agent can move **anywhere** on each floor
- Random waypoint generation
- Natural movement patterns
- Full floor coverage (~80%+)

### ✓ Stair Navigation
- "Blue line" path from floor to stairs
- 12 steps per flight
- Smooth climbing animation
- Proper floor-to-floor transitions

### ✓ Visual Improvements
- Proper camera orientation (floor 0 at bottom)
- Real-time progress display
- Color-coded agent states
- Safe area visualization

---

## 🛠️ Common Tasks

### Run Main Simulation
```bash
python building_navigation_sim.py
```

### Generate New Building
```bash
cd test
python create_4story_advanced.py
```

### Quick Test
```bash
cd test
python test_simple_path.py
```

### View Building
```bash
cd test
python view_building.py
```

### Run All Tests
```bash
cd test
python run_all_tests.py
```

---

## 🔧 Customization

Want to modify the simulation? Edit `building_navigation_sim.py`:

### Change Number of Floors
```python
self.num_floors = 6  # Line ~27
```

### Change Floor Height
```python
self.floor_height = 3.5  # Line ~26
```

### Change Wall Margin
```python
self.wall_margin = 1.5  # Line ~28 (more clearance)
```

### Change Exploration Density
```python
# In calculate_path() function
movement_per_floor = 12  # Line ~97 (more waypoints)
```

---

## ❓ Troubleshooting

### "No building file found"
```bash
cd test
python create_4story_advanced.py
cd ..
python building_navigation_sim.py
```

### AI2Thor won't initialize
Edit `test/create_4story_advanced.py`:
```python
quality='High'  # Change from 'Ultra' (line ~259)
```

### Window won't open
- Check display settings
- Try different terminal
- Verify OpenGL support

### More help
See [BUILDING_DOCUMENTATION.md](BUILDING_DOCUMENTATION.md#troubleshooting)

---

## 📊 What Gets Verified

After simulation completes, you'll see:

```
✓ All 4 floors are accessible
✓ Stairwell connects all floors
✓ Vertical circulation functional
✓ Agent stays within building bounds
✓ Free movement on each floor
✓ All floor waypoints within floor geometry
✓ Floors properly separated
✓ Wall boundaries respected
```

---

## 🎯 Next Steps

1. ✅ **Run the simulation** (you're about to do this!)
2. 📖 **Read README.md** for quick reference
3. 📚 **Browse documentation** for deep dive
4. 🎨 **Customize parameters** to your needs
5. 🏗️ **Generate custom buildings** with different scenes
6. 🎮 **Export for games** (use .stl files)

---

## 📦 Dependencies

```bash
pip install ai2thor pyvista numpy trimesh
```

**Requirements:**
- Python 3.7+
- 4GB+ RAM
- Display with OpenGL
- ~500MB disk space

---

## 📝 Quick Commands

```bash
# Main simulation
python building_navigation_sim.py

# Generate building
cd test && python create_4story_advanced.py && cd ..

# Quick test
cd test && python test_simple_path.py && cd ..

# View building
cd test && python view_building.py && cd ..
```

---

## 🎉 You're Ready!

Run the main simulation:

```bash
python building_navigation_sim.py
```

Choose option **[2]** and enjoy the show!

---

**Version:** 2.0 | **Status:** Production Ready ✓

For help: [README.md](README.md) | [BUILDING_DOCUMENTATION.md](BUILDING_DOCUMENTATION.md)
