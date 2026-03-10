#!/usr/bin/env python3
"""
Attacker simulation example for multi-room, single-story building (first-person view)

Simulates an attacker searching for agents in a realistic multi-room single-story house, 
where the camera can physically navigate between rooms (not just a single room walled off).
"""

from attacker_simulation_framework import AttackerSimulationSingleStory

def main():
    print("=" * 70)
    print("ATTACKER SIMULATION - MULTI-ROOM SINGLE-STORY BUILDING")
    print("First-Person View")
    print("=" * 70)
    print()
    
    # Initialize attacker in a true multi-room floorplan (not just a single isolated room)
    # Example: FloorPlan211 is a large single-story with multiple open/interconnected rooms in AI2THOR.
    attacker = AttackerSimulationSingleStory(
        scene_name='FloorPlan211'  # ensure this is a multi-room house
    )

    # Set up a list of rooms to search; you may expand/modify as appropriate for the floorplan
    # Examples for a real house: Kitchen, LivingRoom, MasterBedroom, Bathroom, DiningRoom, Bedroom
    target_rooms = ['Kitchen', 'LivingRoom', 'MasterBedroom', 'Bathroom', 'DiningRoom', 'Bedroom']
    num_views_per_room = 4  # Fewer viewpoints per room since there are more rooms

    # Gather viewpoints from each accessible room
    viewpoints = []
    for room in target_rooms:
        try:
            room_viewpoints = attacker.get_room_viewpoints(room, num_views_per_room)
        except AttributeError:
            # Fallback if not implemented - just repeat room name (for demonstration)
            room_viewpoints = [room] * num_views_per_room
        viewpoints.extend(room_viewpoints)

    # Interleave room viewpoints so camera moves between rooms naturally
    interleaved = []
    for i in range(num_views_per_room):
        for j in range(len(target_rooms)):
            idx = j * num_views_per_room + i
            interleaved.append(viewpoints[idx])

    try:
        # Perform search, where camera actually moves to each room and viewpoint in a connected floorplan
        attacker.search_for_agents(
            interleaved
        )
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        attacker.cleanup()

    print("Simulation complete!")

if __name__ == "__main__":
    main()
