#!/usr/bin/env python3
"""
Attacker simulation framework for buildings.

Simulates an attacker searching for agents within buildings.
Supports both single-story (first-person) and multi-story (third-person) views.
"""

import numpy as np
import time
import os
from typing import List, Tuple, Optional, Dict
import sys

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../BUILDING'))
from agent_visualization_framework import SingleStoryAgent, MultiStoryAgent

# Lazy imports
pv = None


def _ensure_pyvista():
    """Ensure pyvista is imported"""
    global pv
    if pv is None:
        import pyvista as _pv
        pv = _pv
    return pv


class AttackerSimulationSingleStory:
    """Attacker simulation for single-story building with first-person view"""
    
    def __init__(self, scene_name: str = 'FloorPlan301'):
        """
        Initialize attacker simulation for single-story building
        
        Args:
            scene_name: AI2Thor scene name
        """
        self.agent = SingleStoryAgent(scene_name=scene_name)
        self.search_path = []
        self.found_agents = []  # Will store found agents if any exist
        self.search_radius = 3.0  # Detection radius in meters
        self.step_size = 0.15  # Very small, cautious movement steps
        self.cautious_pause = 0.3  # Pause time between movements for caution
        self.look_around_angles = [0, 45, 90, 135, 180, 225, 270, 315]  # Angles to look around
        self.visited_rooms = set()
    
    def find_kitchen_position(self) -> Optional[Tuple[float, float, float]]:
        """
        Find kitchen position by looking for kitchen-related objects
        
        Returns:
            (x, y, z) position in kitchen, or None if not found
        """
        event = self.agent.controller.step(action='Pass')
        objects = event.metadata.get('objects', [])
        
        # Look for kitchen objects
        kitchen_keywords = ['kitchen', 'refrigerator', 'fridge', 'stove', 'oven', 'microwave', 
                          'counter', 'cabinet', 'sink', 'coffeemachine', 'toaster']
        
        kitchen_objects = []
        for obj in objects:
            obj_type = obj.get('objectType', '').lower()
            obj_name = obj.get('name', '').lower()
            if any(keyword in obj_type or keyword in obj_name for keyword in kitchen_keywords):
                kitchen_objects.append(obj)
        
        if kitchen_objects:
            # Find nearest reachable position to kitchen object
            kitchen_obj = kitchen_objects[0]
            pos = kitchen_obj.get('position', {})
            kitchen_obj_pos = np.array([pos.get('x', 0), pos.get('y', 1.0), pos.get('z', 0)])
            
            # Find nearest reachable position
            reachable = self.agent.get_reachable_positions()
            if reachable:
                positions = np.array([[p['x'], p['y'], p['z']] for p in reachable])
                distances = np.linalg.norm(positions - kitchen_obj_pos, axis=1)
                nearest_idx = np.argmin(distances)
                if distances[nearest_idx] < 3.0:  # Within reasonable distance
                    return tuple(positions[nearest_idx])
        
        # Fallback: look for reachable positions in likely kitchen area
        # Kitchen is often in negative Z area for FloorPlan301
        reachable = self.agent.get_reachable_positions()
        if reachable:
            positions = np.array([[p['x'], p['y'], p['z']] for p in reachable])
            # Kitchen is typically at more negative Z values (back of house)
            z_median = np.median(positions[:, 2])
            kitchen_candidates = positions[positions[:, 2] < z_median - 0.5]  # More negative Z
            if len(kitchen_candidates) > 0:
                # Pick one near the center X of kitchen area
                x_center = np.median(kitchen_candidates[:, 0])
                kitchen_pos = kitchen_candidates[np.argmin(np.abs(kitchen_candidates[:, 0] - x_center))]
                return tuple(kitchen_pos)
        
        return None
    
    def group_positions_by_room(self, positions: np.ndarray) -> Dict[str, List[Tuple[float, float, float]]]:
        """
        Group positions by approximate room/area
        
        Args:
            positions: Array of (x, y, z) positions
            
        Returns:
            Dictionary mapping room names to lists of positions
        """
        rooms = {}
        
        # Use spatial clustering to group positions
        # Simple approach: divide space into regions
        x_min, x_max = positions[:, 0].min(), positions[:, 0].max()
        z_min, z_max = positions[:, 2].min(), positions[:, 2].max()
        
        x_range = x_max - x_min
        z_range = z_max - z_min
        
        # Divide into approximate room regions
        num_x_regions = 3
        num_z_regions = 3
        
        for pos in positions:
            x, y, z = pos[0], pos[1], pos[2]
            
            # Determine which region this position belongs to
            x_region = int((x - x_min) / (x_range / num_x_regions)) if x_range > 0 else 0
            z_region = int((z - z_min) / (z_range / num_z_regions)) if z_range > 0 else 0
            
            # Clamp regions
            x_region = max(0, min(num_x_regions - 1, x_region))
            z_region = max(0, min(num_z_regions - 1, z_region))
            
            room_key = f"room_{x_region}_{z_region}"
            if room_key not in rooms:
                rooms[room_key] = []
            rooms[room_key].append((x, y, z))
        
        return rooms
    
    def open_door_if_needed(self, target_position: Tuple[float, float, float]) -> bool:
        """
        Try to open doors if they're blocking the path
        
        Args:
            target_position: Position we're trying to reach
            
        Returns:
            True if door was opened or no door found, False if blocked
        """
        # Get all objects in scene
        event = self.agent.controller.step(action='Pass')
        all_objects = event.metadata.get('objects', [])
        
        # Look for doors near current position or target
        current_pos = np.array(self.agent.position)
        target_pos = np.array(target_position)
        
        doors_found = []
        for obj in all_objects:
            obj_type = obj.get('objectType', '').lower()
            obj_name = obj.get('name', '').lower()
            
            if 'door' in obj_type or 'door' in obj_name:
                obj_pos = obj.get('position', {})
                obj_pos_array = np.array([obj_pos.get('x', 0), obj_pos.get('y', 0), obj_pos.get('z', 0)])
                
                # Check if door is between current and target, or nearby
                dist_to_current = np.linalg.norm(obj_pos_array - current_pos)
                dist_to_target = np.linalg.norm(obj_pos_array - target_pos)
                
                if dist_to_current < 3.0 or dist_to_target < 3.0:
                    doors_found.append(obj)
        
        # Try to open doors
        for door in doors_found:
            door_id = door.get('objectId', '')
            if not door_id:
                continue
            
            # Check if door is openable and closed
            if door.get('openable', False):
                is_open = door.get('isOpen', False)
                if not is_open:
                    try:
                        # Try to open the door
                        event = self.agent.controller.step({
                            'action': 'OpenObject',
                            'objectId': door_id
                        })
                        if event.metadata.get('lastActionSuccess', False):
                            print(f"  🚪 Opened door: {door.get('name', 'door')}")
                            time.sleep(0.5)  # Pause after opening door
                            return True
                        else:
                            # Try moving closer to door
                            door_pos = door.get('position', {})
                            door_x = door_pos.get('x', 0)
                            door_z = door_pos.get('z', 0)
                            # Move towards door
                            direction = np.array([door_x, 0, door_z]) - current_pos
                            direction = direction / (np.linalg.norm(direction) + 0.001)
                            approach_pos = current_pos + direction * 0.5
                            self.agent.move_to(approach_pos[0], approach_pos[1], approach_pos[2])
                            time.sleep(0.3)
                            # Try opening again
                            event = self.agent.controller.step({
                                'action': 'OpenObject',
                                'objectId': door_id
                            })
                            if event.metadata.get('lastActionSuccess', False):
                                print(f"  🚪 Opened door: {door.get('name', 'door')}")
                                time.sleep(0.5)
                                return True
                    except Exception as e:
                        # Silently continue if door opening fails
                        pass
        
        return True  # No door found or already open
    
    def get_search_waypoints(self) -> List[Tuple[float, float, float, float]]:
        """
        Generate waypoints for systematic ROOM-BY-ROOM search of the ENTIRE building
        Starts in kitchen and goes through all rooms
        
        Returns:
            List of (x, y, z, rotation) waypoints
        """
        reachable = self.agent.get_reachable_positions()
        if not reachable:
            return []
        
        positions = np.array([[p['x'], p['y'], p['z']] for p in reachable])
        
        print(f"Found {len(reachable)} reachable positions in building")
        
        # Group positions by room/area
        rooms = self.group_positions_by_room(positions)
        print(f"Identified {len(rooms)} room/area regions")
        
        # Find kitchen and start there
        kitchen_pos = self.find_kitchen_position()
        if kitchen_pos:
            print(f"Kitchen found at: {kitchen_pos}")
            # Move agent to kitchen
            self.agent.move_to(kitchen_pos[0], kitchen_pos[1], kitchen_pos[2], rotation=0.0)
            time.sleep(0.5)
        else:
            print("Kitchen not found, starting from current position")
            kitchen_pos = tuple(self.agent.position)
        
        # Build waypoints room by room - ensure we visit ALL rooms
        all_waypoints_by_room = {}
        visited_positions = set()
        min_distance_between_waypoints = 0.6  # Minimum distance between waypoints
        
        # Identify kitchen room first
        z_median = np.median(positions[:, 2])
        kitchen_z_threshold = z_median - 0.5  # Kitchen typically at more negative Z
        
        # Group waypoints by room
        for room_name, room_positions in rooms.items():
            room_waypoints = []
            for pos in room_positions:
                x, y, z = pos[0], pos[1], pos[2]
                
                # Check if too close to visited
                too_close = False
                for visited in visited_positions:
                    dist = np.linalg.norm(np.array([x, z]) - np.array([visited[0], visited[2]]))
                    if dist < min_distance_between_waypoints:
                        too_close = True
                        break
                
                if not too_close:
                    room_waypoints.append((x, y, z, 0.0))
                    visited_positions.add((x, y, z))
            
            if room_waypoints:
                all_waypoints_by_room[room_name] = room_waypoints
        
        # Identify which room is kitchen
        kitchen_room = None
        for room_name, room_waypoints in all_waypoints_by_room.items():
            # Check if this room has kitchen-like positions (negative Z)
            room_z_avg = np.mean([wp[2] for wp in room_waypoints])
            if room_z_avg < kitchen_z_threshold:
                kitchen_room = room_name
                break
        
        # If no clear kitchen room, use the one with most negative Z
        if not kitchen_room and all_waypoints_by_room:
            kitchen_room = min(all_waypoints_by_room.keys(), 
                             key=lambda r: np.mean([wp[2] for wp in all_waypoints_by_room[r]]))
        
        # Build ordered path: kitchen first, then other rooms
        ordered_waypoints = []
        
        # Start with kitchen
        if kitchen_room and kitchen_room in all_waypoints_by_room:
            kitchen_waypoints = all_waypoints_by_room[kitchen_room]
            # Order kitchen waypoints starting from kitchen position
            kitchen_array = np.array([kitchen_pos[0], kitchen_pos[2]])
            kitchen_waypoints.sort(key=lambda wp: np.linalg.norm(np.array([wp[0], wp[2]]) - kitchen_array))
            ordered_waypoints.extend(kitchen_waypoints)
            print(f"  🍳 Kitchen room: {len(kitchen_waypoints)} waypoints")
            del all_waypoints_by_room[kitchen_room]
        
        # Visit other rooms systematically
        # Order rooms by proximity to kitchen (visit nearest rooms first)
        remaining_rooms = list(all_waypoints_by_room.items())
        if ordered_waypoints:
            last_wp = ordered_waypoints[-1]
            last_pos = np.array([last_wp[0], last_wp[2]])
            # Sort rooms by distance from last waypoint
            remaining_rooms.sort(key=lambda r: min([np.linalg.norm(np.array([wp[0], wp[2]]) - last_pos) 
                                                   for wp in r[1]]))
        
        for room_name, room_waypoints in remaining_rooms:
            # Order waypoints within room by proximity to last visited waypoint
            if ordered_waypoints:
                last_wp = ordered_waypoints[-1]
                last_pos = np.array([last_wp[0], last_wp[2]])
                room_waypoints.sort(key=lambda wp: np.linalg.norm(np.array([wp[0], wp[2]]) - last_pos))
            else:
                # First room after kitchen - order by proximity to kitchen
                kitchen_array = np.array([kitchen_pos[0], kitchen_pos[2]])
                room_waypoints.sort(key=lambda wp: np.linalg.norm(np.array([wp[0], wp[2]]) - kitchen_array))
            
            ordered_waypoints.extend(room_waypoints)
            print(f"  🚪 Room {room_name}: {len(room_waypoints)} waypoints")
        
        print(f"Generated {len(ordered_waypoints)} waypoints covering {len(remaining_rooms) + (1 if kitchen_room else 0)} rooms")
        
        return ordered_waypoints
    
    def search_for_agents(self, save_views: bool = False):
        """
        Search for agents in the building
        
        Args:
            save_views: Whether to save first-person views during search
        """
        print("=" * 70)
        print("ATTACKER SIMULATION - SINGLE-STORY BUILDING")
        print("=" * 70)
        print("Attacker searching for agents...")
        print()
        
        output_dir = "attacker_views"
        if save_views:
            os.makedirs(output_dir, exist_ok=True)
        
        waypoints = self.get_search_waypoints()
        print(f"Search path: {len(waypoints)} waypoints")
        print()
        
        step_count = 0
        current_room = "kitchen"
        last_room_check = 0
        
        for i, (x, y, z, rotation) in enumerate(waypoints):
            # Detect room transitions
            if i > 0:
                # Check if we've moved to a different room area
                prev_wp = waypoints[i-1]
                prev_pos = np.array([prev_wp[0], prev_wp[2]])
                curr_pos = np.array([x, z])
                distance = np.linalg.norm(curr_pos - prev_pos)
                
                # If moved far, might be entering new room
                if distance > 2.0 and i - last_room_check > 5:
                    # Try to detect which room we're entering
                    reachable = self.agent.get_reachable_positions()
                    if reachable:
                        positions = np.array([[p['x'], p['y'], p['z']] for p in reachable])
                        z_median = np.median(positions[:, 2])
                        if z < z_median - 0.5:
                            new_room = "kitchen"
                        elif z > z_median + 0.5:
                            new_room = "front room"
                        else:
                            new_room = "middle area"
                        
                        if new_room != current_room:
                            print(f"\n  🚪 Entering {new_room}...")
                            current_room = new_room
                            last_room_check = i
                            # Look around when entering new room
                            for look_angle in [90, -90, 180]:
                                self.agent.rotate(look_angle)
                                time.sleep(0.3)
                                nearby_objects = self.agent.get_nearby_objects(radius=self.search_radius)
                                found = self._check_for_agents(nearby_objects)
                                if found:
                                    print(f"  ⚠️  AGENTS DETECTED in {new_room}!")
                                    for agent_info in found:
                                        print(f"     - {agent_info}")
                                    self.found_agents.extend(found)
                            # Return to forward
                            self.agent.rotate(-90 if look_angle == 90 else 90 if look_angle == -90 else -180)
                            time.sleep(0.3)
            # Move to waypoint with CAUTIOUS, small steps
            current_pos = self.agent.position
            target = np.array([x, y, z])
            current = np.array(current_pos)
            
            # Move in small increments
            direction = target - current
            distance = np.linalg.norm(direction)
            
            if distance > 0.1:
                # Calculate rotation to face movement direction
                if distance > 0.2:
                    move_angle = np.arctan2(direction[0], direction[2]) * 180 / np.pi
                    target_rotation = (move_angle + 360) % 360
                else:
                    target_rotation = rotation
                
                # Rotate to face direction first (cautious approach)
                current_rotation = self.agent.rotation
                rotation_diff = (target_rotation - current_rotation + 180) % 360 - 180
                if abs(rotation_diff) > 5:
                    # Rotate gradually
                    if abs(rotation_diff) > 30:
                        rotation_diff = 30 if rotation_diff > 0 else -30
                    self.agent.rotate(rotation_diff)
                    time.sleep(self.cautious_pause * 0.5)  # Pause after rotation
                
                # Move in very small, cautious steps
                num_steps = max(1, int(distance / self.step_size))
                for step in range(num_steps):
                    progress = (step + 1) / num_steps
                    intermediate = current + direction * progress
                    
                    # Try to open doors if needed before moving
                    self.open_door_if_needed(tuple(intermediate))
                    
                    # Move cautiously
                    success = self.agent.move_to(
                        float(intermediate[0]),
                        float(intermediate[1]),
                        float(intermediate[2]),
                        rotation=target_rotation
                    )
                    
                    if not success:
                        # If movement failed, try to open doors and retry
                        print(f"  ⚠️  Movement blocked, checking for doors...")
                        door_opened = self.open_door_if_needed(tuple(intermediate))
                        if door_opened:
                            # Retry movement after opening door
                            time.sleep(0.3)
                            success = self.agent.move_to(
                                float(intermediate[0]),
                                float(intermediate[1]),
                                float(intermediate[2]),
                                rotation=target_rotation
                            )
                        
                        if not success:
                            # Skip this waypoint if still blocked
                            print(f"  ⚠️  Cannot reach position, skipping...")
                            break
                    
                    # CAUTIOUS PAUSE after each step
                    time.sleep(self.cautious_pause)
                    
                    # Look around cautiously (occasionally)
                    if step % 3 == 0 and step > 0:
                        # Quick look left and right
                        self.agent.rotate(30)
                        time.sleep(0.2)
                        nearby_objects = self.agent.get_nearby_objects(radius=self.search_radius)
                        found = self._check_for_agents(nearby_objects)
                        if found:
                            print(f"  ⚠️  AGENTS DETECTED while looking around!")
                            for agent_info in found:
                                print(f"     - {agent_info}")
                            self.found_agents.extend(found)
                        
                        self.agent.rotate(-60)  # Look right
                        time.sleep(0.2)
                        nearby_objects = self.agent.get_nearby_objects(radius=self.search_radius)
                        found = self._check_for_agents(nearby_objects)
                        if found:
                            print(f"  ⚠️  AGENTS DETECTED while looking around!")
                            for agent_info in found:
                                print(f"     - {agent_info}")
                            self.found_agents.extend(found)
                        
                        self.agent.rotate(30)  # Return to forward
                        time.sleep(0.2)
                    
                    # Check for agents at each step
                    nearby_objects = self.agent.get_nearby_objects(radius=self.search_radius)
                    found = self._check_for_agents(nearby_objects)
                    
                    if found:
                        print(f"  ⚠️  AGENTS DETECTED at position ({intermediate[0]:.2f}, {intermediate[1]:.2f}, {intermediate[2]:.2f})!")
                        for agent_info in found:
                            print(f"     - {agent_info}")
                        self.found_agents.extend(found)
                        # Pause longer when agents detected
                        time.sleep(0.5)
                    
                    step_count += 1
                    
                    if save_views and step_count % 5 == 0:
                        view_file = f"{output_dir}/search_step_{step_count:04d}.png"
                        self.agent.save_view(view_file)
            
            # At waypoint: Look around cautiously before moving to next
            if i < len(waypoints) - 1:  # Not at last waypoint
                print(f"  At waypoint {i+1}/{len(waypoints)}: Looking around...")
                # Look in multiple directions
                for look_angle in [45, -45, 90, -90]:
                    self.agent.rotate(look_angle)
                    time.sleep(0.3)
                    nearby_objects = self.agent.get_nearby_objects(radius=self.search_radius)
                    found = self._check_for_agents(nearby_objects)
                    if found:
                        print(f"  ⚠️  AGENTS DETECTED while scanning!")
                        for agent_info in found:
                            print(f"     - {agent_info}")
                        self.found_agents.extend(found)
                
                # Return to forward direction
                next_target = np.array([waypoints[i+1][0], waypoints[i+1][1], waypoints[i+1][2]])
                current_pos_array = np.array(self.agent.position)
                next_direction = next_target - current_pos_array
                next_angle = np.arctan2(next_direction[0], next_direction[2]) * 180 / np.pi
                next_rotation = (next_angle + 360) % 360
                current_rot = self.agent.rotation
                rot_diff = (next_rotation - current_rot + 180) % 360 - 180
                if abs(rot_diff) > 1:
                    self.agent.rotate(rot_diff)
                time.sleep(0.3)  # Pause before moving to next waypoint
            
            # Final check at waypoint
            nearby_objects = self.agent.get_nearby_objects(radius=self.search_radius)
            found = self._check_for_agents(nearby_objects)
            
            if found:
                print(f"  ⚠️  AGENTS DETECTED at waypoint {i+1}!")
                for agent_info in found:
                    print(f"     - {agent_info}")
                self.found_agents.extend(found)
            
            if (i + 1) % 5 == 0:  # More frequent updates
                print(f"  Searched {i+1}/{len(waypoints)} waypoints... ({(i+1)/len(waypoints)*100:.1f}% complete)")
        
        print()
        print("=" * 70)
        print("SEARCH COMPLETE")
        print("=" * 70)
        if self.found_agents:
            print(f"⚠️  FOUND {len(self.found_agents)} AGENT(S):")
            for agent in self.found_agents:
                print(f"   - {agent}")
        else:
            print("✓ No agents found in building")
        print()
    
    def _check_for_agents(self, nearby_objects: List[Dict]) -> List[str]:
        """
        Check if any nearby objects are agents
        
        Args:
            nearby_objects: List of nearby objects from get_nearby_objects
            
        Returns:
            List of agent descriptions if found
        """
        # In a real scenario, you would check for specific agent types
        # For now, we'll check for any human-like or agent-like objects
        agent_keywords = ['agent', 'person', 'human', 'character', 'player']
        found = []
        
        for obj in nearby_objects:
            obj_type = obj.get('type', '').lower()
            obj_name = obj.get('name', '').lower()
            
            # Check if object matches agent keywords
            if any(keyword in obj_type or keyword in obj_name for keyword in agent_keywords):
                found.append(f"{obj.get('type', 'Unknown')} at {obj.get('distance', 0):.2f}m")
        
        return found
    
    def cleanup(self):
        """Clean up resources"""
        self.agent.cleanup()


class AttackerSimulationMultiStory:
    """Attacker simulation for multi-story building with third-person view"""
    
    def __init__(self, building_file: str, floor_height: float = 3.0, num_floors: int = 4):
        """
        Initialize attacker simulation for multi-story building
        
        Args:
            building_file: Path to building mesh file
            floor_height: Height of each floor
            num_floors: Number of floors
        """
        self.agent = MultiStoryAgent(
            building_file=building_file,
            floor_height=floor_height,
            num_floors=num_floors
        )
        self.search_path = []
        self.found_agents = []
        self.search_radius = 4.0  # Detection radius in meters
        self.step_size = 0.3  # Small, controlled movement steps
        self.plotter = None
        self.attacker_marker = None
    
    def get_search_waypoints(self) -> List[Tuple[float, float, float]]:
        """
        Generate waypoints for systematic search of all floors
        
        Returns:
            List of (x, y, z) waypoints
        """
        waypoints = []
        
        # Search each floor systematically
        for floor_num in range(self.agent.num_floors):
            bounds = self.agent.floor_walk_bounds[floor_num]
            floor_y = floor_num * self.agent.floor_height + 0.5
            
            # Create grid search pattern on this floor
            x_range = bounds['x_max'] - bounds['x_min']
            z_range = bounds['z_max'] - bounds['z_min']
            grid_size = 1.5
            
            x_steps = int(x_range / grid_size) + 1
            z_steps = int(z_range / grid_size) + 1
            
            for z_idx in range(z_steps):
                z = bounds['z_min'] + (z_idx / max(1, z_steps - 1)) * z_range
                
                # Zigzag pattern
                if z_idx % 2 == 0:
                    x_list = [bounds['x_min'] + (i / max(1, x_steps - 1)) * x_range for i in range(x_steps)]
                else:
                    x_list = [bounds['x_min'] + (i / max(1, x_steps - 1)) * x_range for i in reversed(range(x_steps))]
                
                for x in x_list:
                    # Ensure within bounds
                    x = max(bounds['x_min'], min(bounds['x_max'], x))
                    z = max(bounds['z_min'], min(bounds['z_max'], z))
                    waypoints.append((x, floor_y, z))
        
        return waypoints
    
    def visualize_setup(self):
        """Setup visualization with building"""
        _ensure_pyvista()
        self.plotter = pv.Plotter()
        
        # Add building mesh
        self.plotter.add_mesh(
            self.agent.building_mesh,
            color='tan',
            opacity=0.3,
            show_edges=True,
            edge_color='gray',
            line_width=0.5,
            label='Building Structure'
        )
        
        # Add floor labels
        for floor in range(self.agent.num_floors):
            floor_y = floor * self.agent.floor_height
            bounds = self.agent.building_mesh.bounds
            self.plotter.add_text(
                f'Floor {floor + 1}',
                position=(bounds[0] - 1, floor_y + self.agent.floor_height/2, bounds[4] - 1),
                font_size=20,
                color='white'
            )
        
        # Setup camera
        bounds = self.agent.building_mesh.bounds
        center_x = (bounds[0] + bounds[1]) / 2
        center_y = (bounds[2] + bounds[3]) / 2
        center_z = (bounds[4] + bounds[5]) / 2
        
        self.plotter.camera_position = [
            (center_x + 20, center_y + 15, center_z + 20),
            (center_x, center_y, center_z),
            (0, 1, 0)
        ]
        
        self.plotter.add_text(
            "Attacker Simulation - Multi-Story Building\nThird-Person View",
            position='upper_left',
            font_size=14,
            color='white'
        )
    
    def update_attacker_visualization(self, position: Tuple[float, float, float], 
                                     floor: int, step: int, total_steps: int):
        """Update attacker position in visualization"""
        # Remove old attacker marker
        if self.attacker_marker:
            try:
                self.plotter.remove_actor('attacker')
            except:
                pass
        
        # Add new attacker marker (red sphere for attacker)
        attacker = pv.Sphere(radius=0.3, center=position)
        self.attacker_marker = attacker
        self.plotter.add_mesh(attacker, color='darkred', name='attacker', opacity=0.95)
        
        # Update status
        try:
            self.plotter.remove_actor('status')
        except:
            pass
        
        found_count = len(self.found_agents)
        status_msg = f"Attacker Search\nFloor: {floor + 1}\nStep: {step}/{total_steps}\nAgents Found: {found_count}"
        if found_count > 0:
            status_msg += "\n⚠️ AGENTS DETECTED!"
        
        self.plotter.add_text(status_msg, position='lower_left', font_size=12, color='yellow', name='status')
        
        # Update camera to follow attacker
        self.plotter.camera.focal_point = position
        self.plotter.camera.position = (
            position[0] + 15,
            position[1] + 10,
            position[2] + 15
        )
    
    def search_for_agents(self):
        """
        Search for agents in the building with visualization
        """
        print("=" * 70)
        print("ATTACKER SIMULATION - MULTI-STORY BUILDING")
        print("=" * 70)
        print("Attacker searching for agents...")
        print()
        
        waypoints = self.get_search_waypoints()
        print(f"Search path: {len(waypoints)} waypoints across {self.agent.num_floors} floors")
        print()
        
        self.visualize_setup()
        self.plotter.show(interactive_update=True, auto_close=False)
        
        # Start at first waypoint
        if waypoints:
            self.agent.spawn_at_floor(0, x=waypoints[0][0], z=waypoints[0][2])
        
        for i, (x, y, z) in enumerate(waypoints):
            current_pos = self.agent.position
            if current_pos is None:
                self.agent.move_to(x, y, z)
                current_pos = [x, y, z]
            
            target = np.array([x, y, z])
            current = np.array(current_pos)
            
            # Move in small increments
            direction = target - current
            distance = np.linalg.norm(direction)
            
            if distance > 0.1:
                num_steps = max(1, int(distance / self.step_size))
                for step in range(num_steps):
                    progress = (step + 1) / num_steps
                    intermediate = current + direction * progress
                    
                    self.agent.move_to(
                        float(intermediate[0]),
                        float(intermediate[1]),
                        float(intermediate[2])
                    )
                    
                    floor = int(intermediate[1] / self.agent.floor_height)
                    
                    # Check for agents (simulated - in real scenario would check actual agent positions)
                    found = self._check_for_agents_at_position(intermediate, floor)
                    
                    if found:
                        print(f"  ⚠️  AGENTS DETECTED at position ({intermediate[0]:.2f}, {intermediate[1]:.2f}, {intermediate[2]:.2f})!")
                        for agent_info in found:
                            print(f"     - {agent_info}")
                        self.found_agents.extend(found)
                    
                    # Update visualization
                    self.update_attacker_visualization(
                        tuple(intermediate),
                        floor,
                        i * num_steps + step + 1,
                        len(waypoints) * num_steps
                    )
                    self.plotter.update()
                    time.sleep(0.05)
            
            # Final check at waypoint
            floor = int(y / self.agent.floor_height)
            found = self._check_for_agents_at_position([x, y, z], floor)
            
            if found:
                print(f"  ⚠️  AGENTS DETECTED at waypoint {i+1} (Floor {floor + 1})!")
                for agent_info in found:
                    print(f"     - {agent_info}")
                self.found_agents.extend(found)
            
            if (i + 1) % 20 == 0:
                print(f"  Searched {i+1}/{len(waypoints)} waypoints...")
        
        # Final message
        final_msg = "Search Complete!\n"
        if self.found_agents:
            final_msg += f"⚠️ FOUND {len(self.found_agents)} AGENT(S)!"
        else:
            final_msg += "✓ No agents found"
        
        self.plotter.add_text(
            final_msg,
            position='upper_edge',
            font_size=16,
            color='red' if self.found_agents else 'green',
            name='complete'
        )
        
        print()
        print("=" * 70)
        print("SEARCH COMPLETE")
        print("=" * 70)
        if self.found_agents:
            print(f"⚠️  FOUND {len(self.found_agents)} AGENT(S):")
            for agent in self.found_agents:
                print(f"   - {agent}")
        else:
            print("✓ No agents found in building")
        print("\nClose the window to exit.")
        self.plotter.show()
    
    def _check_for_agents_at_position(self, position: List[float], floor: int) -> List[str]:
        """
        Check if any agents are at the given position
        
        Args:
            position: (x, y, z) position to check
            floor: Current floor number
            
        Returns:
            List of agent descriptions if found
        """
        # In a real scenario, this would check actual agent positions
        # For now, we simulate by checking if position is near certain areas
        # (In a real implementation, you would maintain a list of agent positions)
        
        # Since there are no agents currently, this will always return empty
        # But the structure is here for when agents are added
        return []
    
    def cleanup(self):
        """Clean up resources"""
        if self.plotter:
            self.plotter.close()
        self.agent.cleanup()

