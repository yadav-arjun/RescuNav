#!/usr/bin/env python3
"""
Fire simulation example for 4-story building (third-person view)

Demonstrates fire expansion through a 4-story building from third-person perspective.
"""

import os
from fire_simulation_framework import FireSimulationMultiStory

def find_building_file():
    """Find available 4-story building file"""
    search_paths = [
        'ai2thor_4story_building.vtk',
        'unified_4story_building.vtk',
        '../ai2thor_4story_building.vtk',
        '../unified_4story_building.vtk',
        '../../ai2thor_4story_building.vtk',
        '../../unified_4story_building.vtk',
        '../../building dev/test/ai2thor_4story_building.vtk',
        '../../building dev/test/unified_4story_building.vtk',
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            return path
    
    return None

def main():
    print("=" * 70)
    print("FIRE SIMULATION - 4-STORY BUILDING")
    print("Third-Person View")
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
    
    # Initialize fire simulation
    # Fire starts on ground floor (floor 0) at center
    fire_sim = FireSimulationMultiStory(
        building_file=building_file,
        fire_start_floor=0,
        fire_start_position=None,  # Will use floor center
        floor_height=3.0,
        num_floors=4
    )
    
    try:
        # Run fire expansion simulation
        fire_sim.simulate_fire_expansion(
            steps=35,
            step_delay=0.25
        )
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        fire_sim.cleanup()
    
    print("Simulation complete!")

if __name__ == "__main__":
    main()

