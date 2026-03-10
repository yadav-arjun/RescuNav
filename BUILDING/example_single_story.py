#!/usr/bin/env python3
"""
Example: Single-story building navigation with first-person view

Shows an agent moving through a single-story building from first-person perspective.
The agent moves through the building and captures views at different locations.
"""

import time
import os
from agent_visualization_framework import SingleStoryAgent

def main():
    print("=" * 70)
    print(" " * 15 + "SINGLE-STORY BUILDING NAVIGATION")
    print(" " * 20 + "First-Person View")
    print("=" * 70)
    print()
    
    # Initialize agent
    print("Initializing single-story building scene...")
    agent = SingleStoryAgent(scene_name='FloorPlan301', width=1920, height=1080)
    print(f"Scene loaded: {agent.scene_name}")
    print(f"Initial position: {agent.position}")
    print()
    
    # Create output directory for views
    output_dir = "single_story_views"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get initial view
    print("Capturing initial view...")
    agent.save_view(f"{output_dir}/view_initial.png")
    print(f"Saved: {output_dir}/view_initial.png")
    print()
    
    # Define a path through the building
    # These coordinates are approximate for FloorPlan301
    path = [
        (0.0, 1.0, -5.0, 0.0),      # Entrance area
        (0.0, 1.0, -2.0, 0.0),      # Move inside
        (2.0, 1.0, 0.0, 90.0),      # Move to stairwell area
        (2.0, 1.0, 2.0, 90.0),      # Continue forward
        (0.0, 1.0, 2.0, 180.0),     # Move to back area
        (-2.0, 1.0, 2.0, 180.0),    # Move to side
        (-2.0, 1.0, 0.0, 270.0),    # Move along side
        (-2.0, 1.0, -2.0, 270.0),   # Continue
        (0.0, 1.0, -2.0, 0.0),      # Return to center
    ]
    
    print("Starting navigation through building...")
    print(f"Path has {len(path)} waypoints")
    print()
    
    # Move through the path
    for i, (x, y, z, rotation) in enumerate(path):
        print(f"Step {i+1}/{len(path)}: Moving to ({x:.1f}, {y:.1f}, {z:.1f})")
        
        # Move agent
        success = agent.move_to(x, y, z, rotation)
        if not success:
            print(f"  ⚠ Warning: Could not move to ({x:.1f}, {y:.1f}, {z:.1f})")
            continue
        
        # Small delay for smooth movement
        time.sleep(0.3)
        
        # Capture view
        view_file = f"{output_dir}/view_step_{i+1:02d}.png"
        agent.save_view(view_file)
        print(f"  ✓ View saved: {view_file}")
        
        # Get nearby objects
        nearby = agent.get_nearby_objects(radius=2.5)
        if nearby:
            print(f"  Nearby objects: {len(nearby)}")
            for obj in nearby[:3]:  # Show first 3
                visibility = "👁️" if obj['visible'] else "  "
                print(f"    {visibility} {obj['type']} - {obj['distance']:.2f}m")
        
        print()
        time.sleep(0.5)
    
    print("=" * 70)
    print("Navigation complete!")
    print(f"All views saved to: {output_dir}/")
    print()
    print("Views captured:")
    for i in range(len(path) + 1):  # +1 for initial view
        if i == 0:
            print(f"  - {output_dir}/view_initial.png")
        else:
            print(f"  - {output_dir}/view_step_{i:02d}.png")
    print()
    
    # Cleanup
    print("Cleaning up...")
    agent.cleanup()
    print("Done!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nNavigation interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

