# 🚀 RescuNav - How to Run

**GitHub Repository:** [https://github.com/yadav-arjun/RescuNav](https://github.com/yadav-arjun/RescuNav)

Complete guide to running all components of the RescuNav AI Rescue Simulation system.

---

## 📋 Prerequisites

```bash
# Install dependencies
pip install -r requirements_rescue.txt

# Or use python command
python -m pip install -r requirements_rescue.txt
```

---

## 🎯 Quick Start Commands

### 1️⃣ **Web UI (Recommended - Main Interface)**

```bash
python web_app.py
```

**Then open in browser:** http://localhost:5000

**Features:**
- Interactive dashboard
- Video upload simulation
- Real-time logs
- Fire visualization
- Agent path tracking

---

### 2️⃣ **Direct Simulation (Command Line)**

#### Fire Scenario
```bash
python rescue_simulation.py --video main.mp4 --scenario fire --iterations 3 --agents 2
```

#### Attacker Scenario
```bash
python rescue_simulation.py --video main.mp4 --scenario attacker --iterations 3 --agents 2
```

#### Without Video (Random Fire Placement)
```bash
python rescue_simulation.py --scenario fire --iterations 5 --agents 3
```

#### Run Until Success
```bash
python rescue_simulation.py --scenario fire --until-success --max-iterations 20
```

#### View Statistics Only
```bash
python rescue_simulation.py --stats-only
```

---

## 🎨 3D Visualizations

### Building Navigation (Agent Paths)
```bash
python BUILDING/example_4story.py
```

**Shows:**
- 4-story building structure
- Agent navigation paths
- Blue line waypoints
- Stairwell connections

---

### Fire Simulation Visualization
```bash
python scenario/fire/fire_4story.py
```

**Shows:**
- Real-time fire spread
- Red fire zones
- Multi-floor propagation
- Heat rising effects

---

### Attacker Simulation Visualization
```bash
python scenario/attacker/attacker_4story.py
```

**Shows:**
- Attacker patrol patterns
- Floor 2-3 movement
- Search behavior
- Threat zones

---

## 🔧 System Tools

### Check Setup Status
```bash
python check_setup.py
```

**Checks:**
- Python version
- Installed packages
- API keys configuration
- Database connection

---

### View MongoDB Database
```bash
python atlas_learning_db.py
```

**Shows:**
- Mission statistics
- Learning data
- Success rates
- Database connection status

---

### Test Video Analysis Only
```bash
python main.py main.mp4
```

**Analyzes:**
- Fire detection
- People detection
- 3D position estimation
- Movement tracking

---

## 📊 All Available Commands

### Rescue Simulation Options

```bash
python rescue_simulation.py [OPTIONS]

Options:
  --scenario {fire,attacker}    Scenario type (default: fire)
  --video PATH                  Video file for fire analysis
  --iterations N                Number of iterations (default: 10)
  --agents N                    Number of agents (default: 3)
  --until-success              Run until rescue succeeds
  --max-iterations N            Max iterations for until-success (default: 50)
  --stats-only                 Show statistics only
```

### Examples

```bash
# Quick test (3 iterations, 2 agents)
python rescue_simulation.py --scenario fire --iterations 3 --agents 2

# Intensive learning (20 iterations, 5 agents)
python rescue_simulation.py --scenario fire --iterations 20 --agents 5

# With video analysis
python rescue_simulation.py --video main.mp4 --scenario fire --iterations 10

# Attacker scenario until success
python rescue_simulation.py --scenario attacker --until-success --max-iterations 30
```

---

## 🧪 Testing & Development

### Test Individual Components

```bash
# Test building navigation
python building_navigator.py

# Test danger simulation
python danger_simulator.py

# Test AI agents
python nemo_rescue_agents.py

# Test database connection
python atlas_learning_db.py
```

### Run All Tests
```bash
cd tests\test
python run_all_tests.py
cd ..\..
```

### View 3D Building Model
```bash
cd tests\test
python view_building.py ..\..\ai2thor_4story_building.vtk
cd ..\..
```

### Building Navigation Simulation
```bash
cd tests
python building_navigation_sim.py
cd ..
```

---

## 🎬 Complete Workflow

### For First-Time Users

```bash
# 1. Check setup
python check_setup.py

# 2. Run web interface (easiest)
python web_app.py
# Open: http://localhost:5000

# 3. Or run direct simulation
python rescue_simulation.py --scenario fire --iterations 3 --agents 2
```

### For Demonstrations

```bash
# 1. Start with fire visualization
python scenario/fire/fire_4story.py

# 2. Show attacker simulation
python scenario/attacker/attacker_4story.py

# 3. Run building navigation
python BUILDING/example_4story.py

# 4. Run full simulation
python rescue_simulation.py --video main.mp4 --scenario fire --iterations 5 --agents 3
```

### For Development/Testing

```bash
# 1. Check setup
python check_setup.py

# 2. Test components
python building_navigator.py
python danger_simulator.py
python nemo_rescue_agents.py

# 3. Run simulation
python rescue_simulation.py --scenario fire --iterations 3

# 4. View results
python rescue_simulation.py --stats-only
```

---

## 🌐 Web UI Features

When you run `python web_app.py`:

1. **Step 1: Upload Video**
   - Click upload area
   - Select video file
   - Wait for upload

2. **Step 2: Start Simulation**
   - Click "Start Simulation"
   - Watch real-time logs
   - See progress updates

3. **Step 3: Fire Visualization**
   - Animated 4-story building
   - Fire particles
   - Child location marker

4. **Step 4: Agent Paths**
   - Agent movement visualization
   - Path tracking
   - Navigation statistics

---

## 📁 Project Structure

```
RescuNav/
├── web_app.py                    # Web interface
├── rescue_simulation.py          # Main simulation engine
├── main.py                       # Video analysis
├── building_navigator.py         # 3D navigation system
├── danger_simulator.py           # Fire/attacker simulation
├── nemo_rescue_agents.py         # AI agents
├── atlas_learning_db.py          # Database integration
├── visualize_rescue.py           # Visualization tools
├── check_setup.py                # Setup checker
│
├── BUILDING/
│   ├── example_4story.py         # Building navigation demo
│   └── example_single_story.py   # Single floor demo
│
├── scenario/
│   ├── fire/
│   │   └── fire_4story.py        # Fire simulation
│   └── attacker/
│       └── attacker_4story.py    # Attacker simulation
│
└── tests/
    ├── building_navigation_sim.py
    └── test/
        ├── run_all_tests.py
        └── view_building.py
```

---

## 🔑 Environment Setup (Optional)

Create `.env` file for full features:

```env
# Fireworks AI (for video analysis)
FIREWORKS_API_KEY=your_api_key_here

# MongoDB Atlas (for learning persistence)
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=building_analysis
```

**Note:** System works without these - features will be limited but functional.

---

## 🐛 Troubleshooting

### "No module named 'X'"
```bash
pip install -r requirements_rescue.txt
```

### "Port 5000 already in use"
```bash
# Kill the process
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### "No building file found"
```bash
cd tests\test
python create_4story_advanced.py
cd ..\..
```

### "MongoDB connection failed"
System works without MongoDB - learning data just won't persist.

### "Fireworks API key not found"
System works without it - fire placement will be random.

---

## 📊 Expected Output

### Simulation Output
```
======================================================================
RESCUE SIMULATION ENGINE
Scenario: FIRE
======================================================================

Initializing 4-story building navigation graph...
Building initialized: 1600 nodes, 3088 connections

======================================================================
ITERATION 1
======================================================================

Agent rescue_agent_0 planned route: 45 steps
Agent rescue_agent_1 planned route: 47 steps
Agent rescue_agent_2 planned route: 43 steps

Agent rescue_agent_1 reached the child!

======================================================================
MISSION SUCCESS! Time: 38.5s
======================================================================
```

### Web UI Output
```
======================================================================
RESCUNAV WEB UI
======================================================================

Starting web server...
Open your browser to: http://localhost:5000

Press Ctrl+C to stop
======================================================================

 * Running on http://127.0.0.1:5000
```

---

## 🎯 Recommended Commands for Demo

```bash
# 1. Web Interface (Best for presentations)
python web_app.py

# 2. Fire Visualization (Visual impact)
python scenario/fire/fire_4story.py

# 3. Full Simulation (Show AI learning)
python rescue_simulation.py --video main.mp4 --scenario fire --iterations 5 --agents 3

# 4. Statistics (Show results)
python rescue_simulation.py --stats-only
```

---

---

## 📞 Quick Reference

| Command | Purpose |
|---------|---------|
| `python web_app.py` | **Main interface** |
| `python rescue_simulation.py` | **Core simulation** |
| `python scenario/fire/fire_4story.py` | **Fire visualization** |
| `python scenario/attacker/attacker_4story.py` | **Attacker visualization** |
| `python BUILDING/example_4story.py` | **Building navigation** |
| `python check_setup.py` | **Setup checker** |
| `python main.py main.mp4` | **Video analysis** |

---

**Ready to start? Run:**

```bash
python web_app.py
```

Then open: **http://localhost:5000**

---

**For command-line simulation:**

```bash
python rescue_simulation.py --video main.mp4 --scenario fire --iterations 3 --agents 2
```

---

🚀 **Happy Rescuing!**
