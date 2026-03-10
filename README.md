# 🚨 RescuNav - AI-Powered Emergency Rescue Simulation

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB%20Atlas-green.svg)](https://www.mongodb.com/cloud/atlas)
[![AI](https://img.shields.io/badge/AI-Fireworks%20AI-orange.svg)](https://fireworks.ai/)

> Transforming Emergency Response from Reactive Guesswork to Proactive Intelligence

RescuNav is an AI-powered emergency rescue simulation system that uses machine learning, 3D navigation, and iterative learning to optimize rescue operations in life-threatening scenarios like building fires and active shooter situations.

---

## 📚 **Quick Links**

- 🎥 **[Watch Demo Video](https://youtu.be/-NdRGTOABeU?si=OtGgGsycr5FVtY7Y)** - See RescuNav in action
- 🚀 **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- 📖 **[How to Run](HOW_TO_RUN.md)** - Complete command reference
- ⚡ **[Quick Commands](QUICK_COMMANDS.md)** - Copy-paste commands
- 🏗️ **[System Overview](SYSTEM_OVERVIEW.md)** - Architecture details

---

## 🎯 Key Features

- 🔥 **Video Analysis** - Real-time fire detection using Fireworks AI
- 🏢 **3D Building Navigation** - 1,600 nodes, 3,088 connections across 4 floors
- 🤖 **Multi-Agent AI Swarm** - Collaborative rescue coordination
- 📊 **Iterative Learning** - Improves with each simulation (100% success rate achieved!)
- 🗺️ **Dynamic Danger Simulation** - Realistic fire spread and threat movement
- 🌐 **Web Interface** - Real-time visualization and control
- 💾 **Cloud Database** - MongoDB Atlas for persistent learning

---

## 🚀 Quick Start

**New to RescuNav? Start here:**

👉 **[Read the Quick Start Guide](QUICKSTART.md)** - 5-minute setup

👉 **[See All Commands](HOW_TO_RUN.md)** - Complete reference

### Prerequisites

- Python 3.11+
- Fireworks AI API key ([Get one here](https://fireworks.ai/))
- MongoDB Atlas account ([Sign up free](https://www.mongodb.com/cloud/atlas/register))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yadav-arjun/RescuNav.git
cd RescuNav

# 2. Install dependencies
pip install -r requirements_rescue.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env and add your API keys

# 4. Run a simulation
python rescue_simulation.py --scenario fire --iterations 5 --agents 3

# 5. Start web interface
python web_app.py
# Open browser to http://localhost:5000
```

---

## 📊 Performance Metrics

Our system has achieved impressive results:

- ✅ **100% Success Rate** (8/8 missions successful)
- ⚡ **15.1s Average Time** to complete rescue
- 🏆 **14.5s Best Time** (fastest rescue)
- 🛡️ **0.02 Minimum Danger** exposure (safest route)
- 🧠 **Continuous Learning** from every attempt

---

## 🎬 Demo

### 🎥 Watch the Prototype in Action
[![RescuNav Demo](https://img.shields.io/badge/▶️_Watch_Demo-YouTube-red?style=for-the-badge&logo=youtube)](https://youtu.be/-NdRGTOABeU?si=OtGgGsycr5FVtY7Y)

**Video Link:** https://youtu.be/-NdRGTOABeU?si=OtGgGsycr5FVtY7Y

### Features
- 🌐 Interactive Web Interface
- 🏢 3D Building Visualization
- 🔥 Real-time Fire Simulation
- 🤖 AI Agent Navigation
- 📊 Learning Analytics Dashboard

**To see the demo:**
```bash
python web_app.py
```
Then open: http://localhost:5000

---

## 🏗️ Architecture

```
Video Analysis (Fireworks AI)
    ↓
3D Building Navigator (A* Pathfinding)
    ↓
Danger Simulator (Fire/Attacker)
    ↓
AI Agent Swarm (Multi-Agent System)
    ↓
Learning Database (MongoDB Atlas)
    ↓
Improved Performance
```

---

## 🔧 Technology Stack

**Backend:**
- Python 3.11
- NetworkX (Graph algorithms)
- NumPy (Numerical computing)
- PyMongo (MongoDB driver)

**AI & ML:**
- Fireworks AI (Video analysis)
- Custom Multi-Agent System
- A* Pathfinding Algorithm
- Iterative Learning

**Database:**
- MongoDB Atlas (Cloud database)
- 3 Collections: missions, trajectories, learning

**Visualization:**
- PyVista (3D visualization)
- Flask (Web framework)
- HTML/CSS/JavaScript

---

## 📖 Documentation

- [How to Run](HOW_TO_RUN.md) - Complete command reference
- [Quick Commands](QUICK_COMMANDS.md) - Quick command reference
- [Quick Start Guide](QUICKSTART.md) - Get started quickly
- [System Overview](SYSTEM_OVERVIEW.md) - Architecture details
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - What was built

---

## 🎯 Use Cases

### 1. Fire Department Training
Train rescue teams with realistic building fire scenarios before real emergencies.

### 2. Building Safety Planning
Test evacuation routes and identify safety weaknesses in building designs.

### 3. Emergency Response Optimization
Develop data-driven rescue strategies based on successful simulations.

### 4. Research & Development
Test AI algorithms and multi-agent coordination in controlled environments.

---

## 🚀 Usage Examples

**For detailed commands and options, see [HOW_TO_RUN.md](HOW_TO_RUN.md)**

### Run Fire Scenario
```bash
python rescue_simulation.py --scenario fire --iterations 10 --agents 3
```

### Run Attacker Scenario
```bash
python rescue_simulation.py --scenario attacker --iterations 5 --agents 2
```

### View 3D Building
```bash
python tests/test/view_building.py ai2thor_4story_building.vtk
```

### Start Web UI
```bash
python web_app.py
```

### View Database Statistics
```bash
python rescue_simulation.py --stats-only
```

---

## 📁 Project Structure

```
rescunav/
├── main.py                      # Video analysis
├── rescue_simulation.py         # Main orchestrator
├── building_navigator.py        # 3D navigation
├── danger_simulator.py          # Fire/attacker simulation
├── nemo_rescue_agents.py        # AI agents
├── atlas_learning_db.py         # MongoDB integration
├── web_app.py                   # Web interface
├── scenario/                    # Scenario-specific code
├── BUILDING/                    # Visualization scripts
├── static/                      # Web assets
├── templates/                   # HTML templates
└── tests/                       # Test scripts
```

---

**Project:** RescuNav  
**Team:** Lottery Ticket Loser 
**GitHub:** [@yadav-arjun](https://github.com/yadav-arjun)  
**Repository:** [https://github.com/yadav-arjun/RescuNav](https://github.com/yadav-arjun/RescuNav)


**Built with ❤️ for saving lives through AI**
