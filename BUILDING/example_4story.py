#!/usr/bin/env python3
"""
Example: 4-story building navigation with third-person view

Shows an agent moving through a 4-story building from third-person perspective.
The agent moves through all floors, using stairs to transition between floors.
"""

import os
from agent_visualization_framework import MultiStoryAgent

def find_building_file():
    """Find available 4-story building file"""
    search_paths = [
        'ai2thor_4story_building.vtk',
        'unified_4story_building.vtk',
        '../building dev/test/ai2thor_4story_building.vtk',
        '../building dev/test/unified_4story_building.vtk',
        'building dev/test/ai2thor_4story_building.vtk',
        'building dev/test/unified_4story_building.vtk',
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            return path
    
    return None

def main():
    print("=" * 70)
    print(" " * 15 + "4-STORY BUILDING NAVIGATION")
    print(" " * 20 + "Third-Person View")
    print("=" * 70)
    print()
    
    # Find building file
    building_file = find_building_file()
    if not building_file:
        print("Error: No 4-story building file found!")
        print()
        print("Please generate a building first:")
        print("  cd building\\ dev/test")
        print("  python create_4story_building.py")
        print("  OR")
        print("  python create_4story_advanced.py")
        print()
        return
    
    print(f"Using building file: {building_file}")
    print()
    
    # Initialize agent
    print("Loading building...")
    try:
        agent = MultiStoryAgent(
            building_file=building_file,
            floor_height=3.0,
            num_floors=4
        )
        print(f"  ✓ Building loaded: {agent.building_mesh.n_points:,} vertices")
        print(f"  ✓ Floors: {agent.num_floors}")
        print()
    except Exception as e:
        print(f"Error loading building: {e}")
        return
    
    # Calculate path through building
    print("Calculating navigation path...")
    path = agent.calculate_path_through_building(movement_per_floor=6)
    print(f"  ✓ Path calculated: {len(path)} waypoints")
    print(f"  ✓ Path covers all {agent.num_floors} floors")
    print()
    
    # Setup visualization
    print("Setting up visualization...")
    agent.visualize_setup(show_path=True, path_points=path)
    print("  ✓ Visualization ready")
    print()
    
    # Animation options
    print("Animation speed options:")
    print("  [1] Fast (0.1s per waypoint)")
    print("  [2] Normal (0.3s per waypoint) - Recommended")
    print("  [3] Slow (0.8s per waypoint)")
    print()
    
    try:
        choice = input("Select speed [1-3, default=2]: ").strip()
        if not choice:
            choice = '2'
    except KeyboardInterrupt:
        print("\n\nExiting...")
        agent.cleanup()
        return
    
    speed_map = {
        '1': 0.1,
        '2': 0.3,
        '3': 0.8
    }
    speed = speed_map.get(choice, 0.3)
    
    print()
    print("=" * 70)
    print("Starting navigation animation...")
    print("Controls:")
    print("  - Rotate: Left-click and drag")
    print("  - Zoom: Scroll wheel")
    print("  - Pan: Right-click and drag")
    print("  - Quit: Press 'q' or close window")
    print("=" * 70)
    print()
    
    try:
        # Animate path
        agent.animate_path(path, speed=speed)
    except KeyboardInterrupt:
        print("\n\nAnimation interrupted by user")
    except Exception as e:
        print(f"\n\nError during animation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.cleanup()
    
    print()
    print("=" * 70)
    print("Navigation complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()

