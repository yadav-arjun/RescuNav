# 🚀 Start RescuNav Web UI

## One-Command Start

```bash
python web_app.py
```

Then open your browser to: **http://localhost:5000**

## What You'll See

### Main Interface

```
┌─────────────────────────────────────────────────────┐
│  🚨 RescuNav                                        │
│  AI-Powered Emergency Rescue Simulation            │
├──────────────────────────────┬──────────────────────┤
│                              │  📋 Simulation Logs  │
│  📹 Step 1: Upload Video     │  ┌────────────────┐ │
│  ┌──────────────────────┐   │  │ Waiting for    │ │
│  │  Click to select     │   │  │ simulation...  │ │
│  │  video file          │   │  │                │ │
│  └──────────────────────┘   │  │                │ │
│                              │  │                │ │
│  🚀 Step 2: Start           │  └────────────────┘ │
│  [Start Simulation]          │                      │
│                              │  [Clear Logs]        │
│  🔥 Step 3: Building        │                      │
│  [Fire Animation]            │                      │
│                              │                      │
│  🎯 Step 4: Agent Paths     │                      │
│  [Agent Movement]            │                      │
└──────────────────────────────┴──────────────────────┘
```

## Step-by-Step Usage

### 1️⃣ Upload Video (Simulated)
- Click upload area
- Select any video file
- Wait 2 seconds for "upload"
- See: ✅ Video uploaded: main.mp4

### 2️⃣ Start Simulation
- Click "Start Simulation" button
- Right panel shows live logs
- Watch simulation progress in real-time

### 3️⃣ View Fire Simulation
- Animated 4-story building appears
- Fire particles show spread
- Purple dot = child on top floor
- Green area = stairwell
- Use Pause/Reset controls

### 4️⃣ View Agent Movement
- Blue robot agent appears
- Watch it navigate the building:
  1. Goes up to middle floors
  2. Waits briefly
  3. Returns to ground
  4. Goes to top floor
  5. Waits briefly
  6. Returns to ground
  7. Repeats cycle
- Blue trail shows path history
- Stats show current phase and position

## What's Happening

### Behind the Scenes

When you click "Start Simulation":

1. **Flask server** starts subprocess
2. **Runs:** `python rescue_simulation.py --scenario fire --iterations 3 --agents 2`
3. **Streams** output to web interface
4. **MongoDB** stores results (if configured)
5. **Visualizations** activate automatically

### Video Analysis Note

The "upload" is **simulated**. The system actually uses:
- **main.mp4** from your project directory
- **Fireworks AI** analyzes frames after frame 6
- **Detects:** Fire, 10 people in danger, 3D positions

## Features You'll See

### Live Logs (Right Panel)
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

Learning from 0 previous attempts
...
```

### Fire Visualization (Step 3)
- **100 fire particles** animated in real-time
- Particles rise and fade realistically
- Building structure clearly visible
- Child location marked
- Stairwell highlighted

### Agent Visualization (Step 4)
- **Smooth movement** at 60 FPS
- **Path tracking** shows historical route
- **Stats display** shows current phase
- **Looping animation** demonstrates navigation

## Quick Tips

### Performance
- Works best in Chrome/Edge
- Animations run at 60 FPS
- Low CPU usage (~5-10%)
- Minimal memory footprint

### Controls
- **Pause/Play** - Stop/resume fire animation
- **Reset** - Restart fire animation
- **Clear Logs** - Clear log panel
- **Auto-scroll** - Logs automatically scroll to bottom

### Color Coding (Logs)
- 🟢 Green = Success/Info
- 🟡 Orange = Warning
- 🔴 Red = Error

## Troubleshooting

### "Address already in use"
```bash
# Kill existing Flask process
lsof -ti:5000 | xargs kill -9

# Then restart
python web_app.py
```

### Simulation doesn't start
1. Check `rescue_simulation.py` exists
2. Ensure dependencies installed
3. Check terminal for errors

### No logs appearing
1. Refresh browser page
2. Check browser console (F12)
3. Verify simulation started

### Animations not showing
1. Enable JavaScript in browser
2. Try different browser (Chrome recommended)
3. Check canvas support

## Advanced

### Change Simulation Parameters

Edit `web_app.py` line 52:
```python
['python', 'rescue_simulation.py',
 '--scenario', 'fire',       # or 'attacker'
 '--iterations', '5',         # increase iterations
 '--agents', '4']             # more agents
```

### Use Real Video

To enable real video processing:
1. Install OpenCV: `pip install opencv-python`
2. Upload will actually process your video
3. Fireworks AI analyzes frames
4. Fire locations based on detection

## Complete Workflow

```
Upload Video → Start Sim → Watch Fire → View Agents → Results
    ↓             ↓            ↓           ↓            ↓
 (Simulated)  (Real code)  (Animation)  (Pathfinding) (MongoDB)
```

## Expected Output

### Console (Terminal)
```
======================================================================
RESCUNAV WEB UI
======================================================================

Starting web server...
Open your browser to: http://localhost:5000

Press Ctrl+C to stop
======================================================================

 * Running on http://127.0.0.1:5000
 * Restarting with stat
```

### Browser
- Clean modern interface
- Purple gradient header
- Split view: simulation (left) + logs (right)
- Animated visualizations
- Real-time updates

## Stop the Server

Press `Ctrl+C` in the terminal to stop the web server.

---

**Ready to start? Run:**

```bash
python web_app.py
```

Then visit: **http://localhost:5000**

Enjoy! 🚀
