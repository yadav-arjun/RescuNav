# How to View the 3D Building Map

## Quick Start

You already have 3D building files generated! Here's how to view them:

### Option 1: View Existing 3D Files (Easiest)

You have these 3D files ready:
- `ai2thor_4story_building.vtk` (VTK format)
- `ai2thor_4story_building.stl` (STL format)  
- `ai2thor_4story_building.ply` (PLY format)

**Command:**
```bash
cd tests/test
python view_building.py ../../ai2thor_4story_building.vtk
```

Or run the interactive viewer:
```bash
cd tests/test
python view_building.py
```
Then select the file from the menu.

### Option 2: Generate New 3D Building

```bash
cd tests/test
python create_4story_building.py
```

This will create a new 4-story building and save it as 3D files.

### Option 3: View in Web Browser (No Installation)

Use online 3D viewers:

1. **For STL files:**
   - Go to: https://www.viewstl.com/
   - Upload: `ai2thor_4story_building.stl`

2. **For PLY files:**
   - Go to: https://3dviewer.net/
   - Upload: `ai2thor_4story_building.ply`

### Option 4: Use Blender (Professional)

1. Download Blender: https://www.blender.org/download/
2. Open Blender
3. File → Import → STL (.stl)
4. Select `ai2thor_4story_building.stl`

## What You'll See

The 3D map shows:
- **4 floors** stacked vertically (Floor 0 at bottom, Floor 3 at top)
- **Rooms** on each floor
- **Stairwells** connecting floors
- **Walls** and structure
- **Navigation grid** (1600 nodes, 3088 connections)

## Building Specifications

```
Dimensions:
- Width: 40m x 40m per floor
- Height: 3m per floor (12m total)
- Grid: 10x10 nodes per floor
- Total nodes: 1600 (400 per floor × 4 floors)
- Connections: 3088 (horizontal + vertical)
```

## Viewer Controls (PyVista)

Once PyVista is installed and you run the viewer:

```
Left-click + drag  : Rotate view
Right-click + drag : Pan/move
Scroll wheel       : Zoom in/out
'r'                : Reset camera
's'                : Take screenshot
'q' or ESC         : Quit
```

## Alternative: Simple Text Visualization

If you just want to see the structure without 3D graphics:

```bash
python building_navigator.py
```

This will print the building structure in text format.

## Troubleshooting

### PyVista not installed?
```bash
pip install pyvista
```

### Can't see the 3D window?
- Make sure you're not running in a remote/SSH session
- PyVista requires a display/GUI environment
- Use the web browser option instead

### File not found?
Make sure you're in the correct directory:
```bash
# Check current directory
dir

# You should see the .vtk, .stl, or .ply files
# If not, run from the main project folder
cd C:\Users\hp\Desktop\rescunav-main\rescunav-main
```

## Quick Test

Run this to see if everything works:

```bash
# Test 1: Check if files exist
dir ai2thor_4story_building.*

# Test 2: View the building
cd tests\test
python view_building.py ..\..\ai2thor_4story_building.vtk
```

## For Hackathon Presentation

**Best option for demo:**
1. Use online viewer (https://www.viewstl.com/)
2. Upload `ai2thor_4story_building.stl`
3. Rotate and show the 4-story structure
4. Take screenshots for your presentation

**Or use Blender** for professional-looking renders!
