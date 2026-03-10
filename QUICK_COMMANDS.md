# 🚀 RescuNav - Quick Command Reference

**GitHub Repository:** [https://github.com/yadav-arjun/RescuNav](https://github.com/yadav-arjun/RescuNav)

## Main Commands (Copy & Paste)

### 1. Web UI (Recommended)
```bash
python web_app.py
```
Then open: http://localhost:5000

---

### 2. Fire Simulation
```bash
python rescue_simulation.py --video main.mp4 --scenario fire --iterations 3 --agents 2
```

---

### 3. Attacker Simulation
```bash
python rescue_simulation.py --video main.mp4 --scenario attacker --iterations 3 --agents 2
```

---

### 4. Building Navigation Visualization
```bash
python BUILDING/example_4story.py
```

---

### 5. Fire Visualization
```bash
python scenario/fire/fire_4story.py
```

---

### 6. Attacker Visualization
```bash
python scenario/attacker/attacker_4story.py
```

---

### 7. Check Setup
```bash
python check_setup.py
```

---

### 8. View Database
```bash
python atlas_learning_db.py
```

---

### 9. Video Analysis Only
```bash
python main.py main.mp4
```

---

## Quick Test Commands

```bash
# Test all components
python check_setup.py

# Quick simulation (3 iterations)
python rescue_simulation.py --scenario fire --iterations 3 --agents 2

# View statistics
python rescue_simulation.py --stats-only
```

---

## For Demonstrations

```bash
# 1. Start web interface
python web_app.py

# 2. Show fire visualization
python scenario/fire/fire_4story.py

# 3. Show attacker simulation
python scenario/attacker/attacker_4story.py

# 4. Run full simulation
python rescue_simulation.py --video main.mp4 --scenario fire --iterations 5 --agents 3
```

---

## Installation

```bash
# Install dependencies
pip install -r requirements_rescue.txt
```

---

## Alternative Python Commands

Your system supports all three:
```bash
python web_app.py    # Standard (recommended)
py web_app.py        # Windows Python Launcher
py -3.11 web_app.py  # Specific Python version
```

---

For detailed documentation, see: **HOW_TO_RUN.md**
