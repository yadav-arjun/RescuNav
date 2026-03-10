#!/usr/bin/env python3
"""
Fire simulation framework for buildings.

Simulates fire expansion through buildings with red-colored surfaces.
Supports both single-story (first-person) and multi-story (third-person) views.
"""

import numpy as np
import time
import os
from typing import List, Tuple, Optional, Dict
import sys
import cv2

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


class FireSimulationSingleStory:
    """Fire simulation for single-story building with first-person view"""
    
    def __init__(self, scene_name: str = 'FloorPlan301', fire_start_position: Optional[Tuple[float, float, float]] = None):
        """
        Initialize fire simulation for single-story building
        
        Args:
            scene_name: AI2Thor scene name
            fire_start_position: (x, y, z) where fire starts. If None, uses center of building.
        """
        self.agent = SingleStoryAgent(scene_name=scene_name)
        self.fire_positions = []
        self.fire_start = fire_start_position
        self.base_expansion_rate = 0.4  # base expansion rate in meters per step
        self.max_fire_radius = 8.0  # maximum fire spread radius
        
        # Material flammability factors (higher = faster spread)
        self.material_flammability = {
            'wood': 2.5,      # Very flammable
            'Wood': 2.5,
            'carpet': 2.0,    # Flammable
            'Carpet': 2.0,
            'rug': 2.0,       # Flammable
            'Rug': 2.0,
            'fabric': 1.8,    # Flammable
            'Fabric': 1.8,
            'cloth': 1.8,     # Flammable
            'Cloth': 1.8,
            'paper': 2.2,     # Very flammable
            'Paper': 2.2,
            'cardboard': 2.0, # Flammable
            'Cardboard': 2.0,
            'plastic': 1.5,   # Moderately flammable
            'Plastic': 1.5,
            'metal': 0.3,     # Not flammable
            'Metal': 0.3,
            'glass': 0.2,     # Not flammable
            'Glass': 0.2,
            'ceramic': 0.2,   # Not flammable
            'Ceramic': 0.2,
            'concrete': 0.1,  # Not flammable
            'Concrete': 0.1,
            'default': 1.0    # Default spread rate
        }
        
        if self.fire_start is None:
            # Get reachable positions and use center
            reachable = self.agent.get_reachable_positions()
            if reachable:
                positions = np.array([[p['x'], p['y'], p['z']] for p in reachable])
                self.fire_start = (
                    float(np.mean(positions[:, 0])),
                    float(np.mean(positions[:, 1])),
                    float(np.mean(positions[:, 2]))
                )
            else:
                self.fire_start = (0.0, 1.0, 0.0)
        
        self.fire_positions.append(self.fire_start)
    
    def get_material_at_position(self, position: Tuple[float, float, float]) -> float:
        """
        Detect material type at a position and return flammability factor
        
        Args:
            position: (x, y, z) position to check
            
        Returns:
            Flammability factor (0.1 to 2.5)
        """
        # Get nearby objects to determine material
        nearby_objects = self.agent.get_nearby_objects(radius=1.5)
        
        max_flammability = 1.0  # Default
        
        for obj in nearby_objects:
            obj_type = obj.get('type', '').lower()
            obj_name = obj.get('name', '').lower()
            
            # Check object type and name for material keywords
            for material, factor in self.material_flammability.items():
                if material.lower() in obj_type or material.lower() in obj_name:
                    max_flammability = max(max_flammability, factor)
                    break
        
        # Also check for common burnable furniture/objects
        burnable_keywords = ['chair', 'table', 'sofa', 'couch', 'bed', 'desk', 
                           'cabinet', 'shelf', 'book', 'curtain', 'drape']
        for keyword in burnable_keywords:
            for obj in nearby_objects:
                obj_type = obj.get('type', '').lower()
                obj_name = obj.get('name', '').lower()
                if keyword in obj_type or keyword in obj_name:
                    max_flammability = max(max_flammability, 1.8)  # Furniture is flammable
                    break
        
        return max_flammability
    
    def project_fire_to_screen(self, fire_position: Tuple[float, float, float], 
                              frame_width: int, frame_height: int) -> Optional[Tuple[int, int]]:
        """
        Project 3D fire position to 2D screen coordinates using AI2Thor camera info
        
        Args:
            fire_position: (x, y, z) world position
            frame_width: Frame width
            frame_height: Frame height
            
        Returns:
            (x, y) screen coordinates or None if not visible
        """
        # Get current event to access camera metadata
        event = self.agent.controller.step(action='Pass')
        agent_meta = event.metadata['agent']
        
        # Get agent position and camera info
        agent_pos = np.array([
            agent_meta['position']['x'],
            agent_meta['position']['y'],
            agent_meta['position']['z']
        ])
        fire_pos = np.array(fire_position)
        
        # Calculate relative position
        relative = fire_pos - agent_pos
        distance = np.linalg.norm(relative)
        
        if distance > 25.0 or distance < 0.1:  # Increased visibility range significantly
            return None
        
        # Get camera rotation
        rotation_y = agent_meta['rotation']['y']
        horizon = agent_meta['cameraHorizon']
        
        # Calculate direction vectors
        rot_rad = np.radians(rotation_y)
        forward = np.array([np.sin(rot_rad), 0, np.cos(rot_rad)])
        right = np.array([np.cos(rot_rad), 0, -np.sin(rot_rad)])
        up = np.array([0, 1, 0])
        
        # Project relative position onto camera basis
        forward_dist = np.dot(relative, forward)
        right_dist = np.dot(relative, right)
        up_dist = np.dot(relative, up)
        
        # Check if in front of camera
        if forward_dist < 0.1:  # Behind or too close (reduced threshold)
            return None
        
        # Apply horizon adjustment
        horizon_rad = np.radians(horizon)
        up_adjusted = up_dist * np.cos(horizon_rad) - forward_dist * np.sin(horizon_rad)
        
        # Perspective projection (simplified FOV calculation)
        # AI2Thor typically uses ~60-90 degree FOV
        fov_rad = np.radians(70)  # Approximate FOV
        fov_factor = 1.0 / np.tan(fov_rad / 2)
        
        # Convert to normalized device coordinates
        ndc_x = (right_dist / forward_dist) * fov_factor
        ndc_y = (up_adjusted / forward_dist) * fov_factor
        
        # Convert to screen coordinates
        screen_x = int(frame_width / 2 + ndc_x * frame_width / 2)
        screen_y = int(frame_height / 2 - ndc_y * frame_height / 2)
        
        # Check if within screen bounds
        if 0 <= screen_x < frame_width and 0 <= screen_y < frame_height:
            return (screen_x, screen_y)
        
        return None
    
    def overlay_fire_on_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Overlay fire visualization on the frame with LARGE, VISIBLE glowing spheres
        
        Args:
            frame: Input frame from AI2Thor
            
        Returns:
            Frame with fire overlays
        """
        frame_with_fire = frame.copy()
        frame_height, frame_width = frame.shape[:2]
        
        import random
        visible_fires = 0
        
        # Draw BIG fire spheres at each fire position
        # Also draw fires that might be slightly off-screen to ensure visibility
        for fire_pos in self.fire_positions:
            screen_pos = self.project_fire_to_screen(fire_pos, frame_width, frame_height)
            
            # If projection failed, try to draw anyway if fire is nearby
            if not screen_pos:
                # Check distance - if very close, draw at center of screen
                event = self.agent.controller.step(action='Pass')
                agent_meta = event.metadata['agent']
                agent_pos = np.array([
                    agent_meta['position']['x'],
                    agent_meta['position']['y'],
                    agent_meta['position']['z']
                ])
                fire_pos_array = np.array(fire_pos)
                distance = np.linalg.norm(fire_pos_array - agent_pos)
                
                # If fire is very close (within 3m), draw it anyway
                if distance < 3.0:
                    # Draw at approximate center with offset based on relative position
                    relative = fire_pos_array - agent_pos
                    x = int(frame_width / 2 + relative[0] * 50)  # Scale factor
                    y = int(frame_height / 2 - relative[2] * 50)
                    screen_pos = (x, y)
            
            if screen_pos:
                x, y = screen_pos
                # Clamp to screen bounds
                x = max(0, min(frame_width - 1, x))
                y = max(0, min(frame_height - 1, y))
                visible_fires += 1
                
                # Get material flammability to adjust fire size
                flammability = self.get_material_at_position(fire_pos)
                size_multiplier = max(2.0, flammability)  # Much larger base size
                
                # MUCH LARGER fire spheres - base size of 80-150 pixels
                base_size = int(80 + (flammability - 1.0) * 30)  # 80-140 pixels base
                base_size = min(base_size, 200)  # Cap at 200 pixels
                
                # Create BIG, VISIBLE fire glow effect with multiple layers
                # Outer glow (red) - MUCH MORE VISIBLE
                overlay = frame_with_fire.copy()
                cv2.circle(overlay, (x, y), base_size + 30, (0, 0, 255), -1)
                cv2.addWeighted(overlay, 0.6, frame_with_fire, 0.4, 0, frame_with_fire)  # More opaque
                
                # Middle glow (orange-red) - MORE VISIBLE
                overlay = frame_with_fire.copy()
                cv2.circle(overlay, (x, y), base_size + 20, (0, 30, 255), -1)
                cv2.addWeighted(overlay, 0.7, frame_with_fire, 0.3, 0, frame_with_fire)
                
                # Inner glow (orange) - MORE VISIBLE
                overlay = frame_with_fire.copy()
                cv2.circle(overlay, (x, y), base_size + 10, (0, 80, 255), -1)
                cv2.addWeighted(overlay, 0.75, frame_with_fire, 0.25, 0, frame_with_fire)
                
                # Core (yellow-orange) - BIG AND BRIGHT
                overlay = frame_with_fire.copy()
                cv2.circle(overlay, (x, y), base_size, (0, 120, 255), -1)
                cv2.addWeighted(overlay, 0.8, frame_with_fire, 0.2, 0, frame_with_fire)
                
                # Bright center (yellow-white) - VERY BRIGHT
                cv2.circle(frame_with_fire, (x, y), max(30, base_size - 20), (0, 180, 255), -1)
                cv2.circle(frame_with_fire, (x, y), max(20, base_size - 40), (0, 220, 255), -1)
                cv2.circle(frame_with_fire, (x, y), max(10, base_size - 60), (0, 255, 255), -1)
                
                # Add flickering effect with larger movement
                for _ in range(3):  # Multiple flicker points
                    flicker_x = x + random.randint(-10, 10)
                    flicker_y = y + random.randint(-10, 10)
                    if 0 <= flicker_x < frame_width and 0 <= flicker_y < frame_height:
                        flicker_size = max(15, base_size - 70)
                        cv2.circle(frame_with_fire, (flicker_x, flicker_y), flicker_size, (0, 255, 255), -1)
        
        # Don't limit - show all fires
        return frame_with_fire
    
    def simulate_fire_expansion(self, steps: int = 20, step_delay: float = 0.5, save_views: bool = True):
        """
        Simulate fire expansion through the building
        
        Args:
            steps: Number of expansion steps
            step_delay: Delay between steps in seconds
            save_views: Whether to save first-person views
        """
        output_dir = "fire_views"
        if save_views:
            os.makedirs(output_dir, exist_ok=True)
        
        print("=" * 70)
        print("FIRE SIMULATION - SINGLE-STORY BUILDING")
        print("=" * 70)
        print(f"Fire starting at: {self.fire_start}")
        print(f"Expansion steps: {steps}")
        print()
        
        # Position agent INSIDE the house to OBSERVE the fire
        # Fire expands independently - agent just watches it
        reachable = self.agent.get_reachable_positions()
        if reachable:
            # Find a position inside the house, offset from fire start for good viewing angle
            positions = np.array([[p['x'], p['y'], p['z']] for p in reachable])
            
            # Find positions that are inside and have good view of fire area
            # Try to be 3-5 meters away from fire start, inside the building
            fire_start_array = np.array(self.fire_start)
            distances = np.linalg.norm(positions - fire_start_array, axis=1)
            
            # Find positions that are 3-5m away and inside
            good_positions = positions[(distances >= 3.0) & (distances <= 5.0)]
            
            if len(good_positions) > 0:
                # Pick one that's likely inside (not at edges)
                center = np.mean(positions, axis=0)
                center_distances = np.linalg.norm(good_positions - center, axis=1)
                best_idx = np.argmin(center_distances)
                agent_pos = good_positions[best_idx]
                
                # Calculate rotation to look at fire initially
                direction = fire_start_array - agent_pos
                angle = np.arctan2(direction[0], direction[2]) * 180 / np.pi
                rotation = (angle + 360) % 360
                
                self.agent.move_to(
                    float(agent_pos[0]),
                    float(agent_pos[1]),
                    float(agent_pos[2]),
                    rotation=rotation
                )
            else:
                # Fallback: move to a position offset from fire start
                self.agent.move_to(
                    self.fire_start[0] - 3.0,
                    self.fire_start[1],
                    self.fire_start[2] - 2.0,
                    rotation=45.0
                )
        else:
            # Fallback positioning
            self.agent.move_to(
                self.fire_start[0] - 3.0,
                self.fire_start[1],
                self.fire_start[2] - 2.0,
                rotation=45.0
            )
        
        # Initial fire is already in fire_positions
        # Fire will expand independently from this point
        print("Fire simulation starting...")
        print("Fire will expand independently - agent camera will track it")
        time.sleep(0.5)
        
        current_fire_points = [self.fire_start]
        
        for step in range(steps):
            print(f"Step {step + 1}/{steps}: Fire expanding...")
            
            # Show material information for current fire points
            if step % 5 == 0 and len(current_fire_points) > 0:
                sample_point = current_fire_points[0]
                flammability = self.get_material_at_position(sample_point)
                material_type = "Highly Flammable" if flammability > 2.0 else "Flammable" if flammability > 1.5 else "Moderately Flammable" if flammability > 1.0 else "Low Flammability"
                print(f"  Material detected: {material_type} (factor: {flammability:.2f})")
            
            # Expand fire to nearby positions
            new_fire_points = []
            for fire_point in current_fire_points:
                # Get material flammability at current fire point
                flammability = self.get_material_at_position(fire_point)
                
                # Calculate expansion rate based on material
                expansion_rate = self.base_expansion_rate * flammability
                expansion_radius = min(expansion_rate * (step + 1) * 0.3, self.max_fire_radius)
                
                # Increase number of expansion directions for more fire points
                num_directions = max(16, int(16 * flammability))  # More directions for flammable materials
                
                for angle in np.linspace(0, 2 * np.pi, num_directions):
                    # Add some randomness for more natural spread
                    angle_offset = np.random.uniform(-0.2, 0.2)
                    radius_variation = np.random.uniform(0.7, 1.0)
                    
                    # Horizontal expansion (floor)
                    x = fire_point[0] + expansion_radius * radius_variation * np.cos(angle + angle_offset)
                    z = fire_point[2] + expansion_radius * radius_variation * np.sin(angle + angle_offset)
                    y = fire_point[1]  # Floor level
                    
                    # Also add vertical expansion (climbing walls)
                    # Fire can climb up walls
                    for height_offset in [0, 0.5, 1.0, 1.5, 2.0, 2.5]:  # Climb up to 2.5m
                        if height_offset > 0:  # Only add vertical points for wall climbing
                            wall_y = fire_point[1] + height_offset
                            # Add fire point on wall at this height
                            wall_point = (x, wall_y, z)
                            
                            # Check if position is reachable (for walls, we check nearby)
                            reachable = self.agent.get_reachable_positions()
                            if reachable:
                                positions = np.array([[p['x'], p['y'], p['z']] for p in reachable])
                                # For wall points, find nearest horizontal position
                                wall_distances = np.linalg.norm(positions[:, [0, 2]] - np.array([x, z]), axis=1)
                                nearest_wall_idx = np.argmin(wall_distances)
                                if wall_distances[nearest_wall_idx] < 1.5:
                                    # Create wall fire point
                                    wall_fire_point = (x, wall_y, z)
                                    
                                    # Check if not too close to existing fire
                                    too_close_wall = False
                                    for existing in self.fire_positions:
                                        if np.linalg.norm(np.array(wall_fire_point) - np.array(existing)) < 0.5:
                                            too_close_wall = True
                                            break
                                    
                                    if not too_close_wall and wall_fire_point not in self.fire_positions:
                                        self.fire_positions.append(wall_fire_point)
                                        new_fire_points.append(wall_fire_point)
                    
                    # Check if position is reachable
                    reachable = self.agent.get_reachable_positions()
                    if reachable:
                        # Find nearest reachable position
                        positions = np.array([[p['x'], p['y'], p['z']] for p in reachable])
                        distances = np.linalg.norm(positions - np.array([x, y, z]), axis=1)
                        nearest_idx = np.argmin(distances)
                        if distances[nearest_idx] < 1.8:  # Within reasonable distance
                            new_point = tuple(positions[nearest_idx])
                            
                            # Check material at new point - if highly flammable, spread faster
                            new_flammability = self.get_material_at_position(new_point)
                            
                            # Check if not too close to existing fire
                            too_close = False
                            min_distance = 0.6 if new_flammability > 1.5 else 0.8
                            for existing in self.fire_positions:
                                if np.linalg.norm(np.array(new_point) - np.array(existing)) < min_distance:
                                    too_close = True
                                    break
                            
                            if not too_close and new_point not in self.fire_positions:
                                new_fire_points.append(new_point)
                                self.fire_positions.append(new_point)
                                
                                # If material is very flammable, add extra fire points nearby
                                if new_flammability > 2.0:
                                    for extra_angle in np.linspace(0, 2 * np.pi, 4):
                                        extra_x = new_point[0] + 0.3 * np.cos(extra_angle)
                                        extra_z = new_point[2] + 0.3 * np.sin(extra_angle)
                                        extra_y = new_point[1]
                                        extra_distances = np.linalg.norm(positions - np.array([extra_x, extra_y, extra_z]), axis=1)
                                        extra_nearest = np.argmin(extra_distances)
                                        if extra_distances[extra_nearest] < 0.5:
                                            extra_point = tuple(positions[extra_nearest])
                                            if extra_point not in self.fire_positions:
                                                self.fire_positions.append(extra_point)
                                                new_fire_points.append(extra_point)
            
            current_fire_points.extend(new_fire_points)
            
            # Update agent camera to track fire expansion - THIS HAPPENS EVERY STEP
            # DO THIS BEFORE capturing the frame so camera is positioned correctly
            # Fire expands on its own - camera automatically follows to observe it
            # ALWAYS update camera if we have fire positions
            if len(self.fire_positions) >= 1:
                # Calculate fire center (where fire is currently expanding)
                # Use recent fire points to track expansion direction
                if len(self.fire_positions) == 1:
                    # If only one fire point, use it directly
                    fire_center = np.array(self.fire_positions[0])
                else:
                    recent_fires = self.fire_positions[-min(30, len(self.fire_positions)):]
                    fire_center = np.mean([np.array(p) for p in recent_fires], axis=0)
                
                # Agent position (camera position) - agent doesn't move, only camera rotates
                current_pos = np.array(self.agent.position)
                direction = fire_center - current_pos
                
                # Calculate angle to look at fire center
                angle = np.arctan2(direction[0], direction[2]) * 180 / np.pi
                target_rotation = (angle + 360) % 360
                
                # Get current rotation
                current_rotation = self.agent.rotation
                
                # Calculate rotation difference (handle wrap-around)
                rotation_diff = (target_rotation - current_rotation + 180) % 360 - 180
                
                # Rotate camera to follow fire (limit speed for smoothness)
                if abs(rotation_diff) > 0.1:  # Rotate even for small differences
                    # Limit rotation speed (max 30 degrees per step for more responsive tracking)
                    if abs(rotation_diff) > 30:
                        rotation_diff = 30 if rotation_diff > 0 else -30
                    
                    # ACTUALLY ROTATE THE CAMERA - THIS MUST HAPPEN
                    old_rotation = self.agent.rotation
                    self.agent.rotate(rotation_diff)
                    new_rotation = self.agent.rotation
                    
                    # Debug: print rotation change every few steps
                    if step % 2 == 0:  # Print every 2 steps
                        print(f"  📹 Camera rotating: {old_rotation:.1f}° -> {new_rotation:.1f}° (target: {target_rotation:.1f}°, diff: {rotation_diff:.1f}°)")
                
                # Also adjust horizon to look at fire if it's climbing walls
                fire_max_height = max([p[1] for p in recent_fires])
                fire_min_height = min([p[1] for p in recent_fires])
                height_range = fire_max_height - fire_min_height
                fire_avg_height = np.mean([p[1] for p in recent_fires])
                
                # Adjust camera horizon based on fire height
                height_diff = fire_avg_height - current_pos[1]
                current_horizon = self.agent.horizon
                
                # Calculate target horizon based on fire height
                target_horizon = min(30, max(-20, height_diff * 10))
                horizon_diff = target_horizon - current_horizon
                
                if abs(horizon_diff) > 0.3:  # Adjust if there's a difference
                    # Limit horizon change speed
                    horizon_change = min(5, max(-5, horizon_diff * 0.5))
                    old_horizon = self.agent.horizon
                    self.agent.look(horizon_change)
                    new_horizon = self.agent.horizon
                    
                    # Debug: print horizon change
                    if step % 2 == 0 and abs(horizon_change) > 0.5:
                        print(f"  📹 Camera horizon: {old_horizon:.1f}° -> {new_horizon:.1f}° (target: {target_horizon:.1f}°, change: {horizon_change:.1f}°)")
            
            # Get frame and overlay fire visualization
            frame = self.agent.get_first_person_view()
            frame_with_fire = self.overlay_fire_on_frame(frame)
            
            # Save view with fire overlay
            if save_views:
                view_file = f"{output_dir}/fire_step_{step+1:02d}.png"
                cv2.imwrite(view_file, cv2.cvtColor(frame_with_fire, cv2.COLOR_RGB2BGR))
                print(f"  View saved: {view_file}")
            
            # Count visible fires
            frame = self.agent.get_first_person_view()
            frame_height, frame_width = frame.shape[:2]
            visible_count = 0
            for fire_pos in self.fire_positions:
                screen_pos = self.project_fire_to_screen(fire_pos, frame_width, frame_height)
                if screen_pos:
                    visible_count += 1
            
            print(f"  Total fire points: {len(self.fire_positions)} | Visible in view: {visible_count}")
            if len(new_fire_points) > 0:
                # Calculate average flammability of new points
                sample_points = new_fire_points[:min(10, len(new_fire_points))]
                avg_flammability = np.mean([self.get_material_at_position(p) for p in sample_points])
                material_desc = "Highly Flammable" if avg_flammability > 2.0 else "Flammable" if avg_flammability > 1.5 else "Moderate"
                print(f"  New fire points: {len(new_fire_points)} (material: {material_desc}, factor: {avg_flammability:.2f})")
            time.sleep(step_delay)
        
        print()
        print("=" * 70)
        print("Fire simulation complete!")
        print(f"Total fire points: {len(self.fire_positions)}")
        print("Fire expanded independently - agent observed the expansion")
        if save_views:
            print(f"Views saved to: {output_dir}/")
        print("=" * 70)
    
    def cleanup(self):
        """Clean up resources"""
        self.agent.cleanup()


class FireSimulationMultiStory:
    """Fire simulation for multi-story building with third-person view"""
    
    def __init__(self, building_file: str, fire_start_floor: int = 0, 
                 fire_start_position: Optional[Tuple[float, float, float]] = None,
                 floor_height: float = 3.0, num_floors: int = 4):
        """
        Initialize fire simulation for multi-story building
        
        Args:
            building_file: Path to building mesh file
            fire_start_floor: Floor where fire starts (0-indexed)
            fire_start_position: (x, y, z) where fire starts. If None, uses floor center.
            floor_height: Height of each floor
            num_floors: Number of floors
        """
        self.agent = MultiStoryAgent(
            building_file=building_file,
            floor_height=floor_height,
            num_floors=num_floors
        )
        self.fire_positions = []
        self.fire_meshes = []  # Store fire visualization meshes
        self.fire_start_floor = fire_start_floor
        self.fire_start = fire_start_position
        self.expansion_rate = 0.5  # meters per step
        self.max_fire_radius = 8.0  # maximum fire spread radius
        self.plotter = None
        
        if self.fire_start is None:
            # Use center of starting floor
            bounds = self.agent.floor_walk_bounds[fire_start_floor]
            self.fire_start = (
                (bounds['x_min'] + bounds['x_max']) / 2,
                fire_start_floor * floor_height + 0.5,
                (bounds['z_min'] + bounds['z_max']) / 2
            )
        
        self.fire_positions.append(self.fire_start)
    
    def create_fire_mesh(self, position: Tuple[float, float, float], radius: float = 0.5):
        """Create a red sphere mesh representing fire at a position"""
        _ensure_pyvista()
        fire_sphere = pv.Sphere(radius=radius, center=position)
        return fire_sphere
    
    def visualize_setup(self):
        """Setup visualization with building and initial fire"""
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
            "Fire Simulation - Multi-Story Building\nThird-Person View",
            position='upper_left',
            font_size=14,
            color='white'
        )
    
    def update_fire_visualization(self, step: int, total_steps: int):
        """Update fire visualization in plotter"""
        # Remove old fire meshes
        for i in range(len(self.fire_meshes)):
            try:
                self.plotter.remove_actor(f'fire_{i}')
            except:
                pass
        
        self.fire_meshes = []
        
        # Add fire meshes for all fire positions
        for i, fire_pos in enumerate(self.fire_positions):
            fire_mesh = self.create_fire_mesh(fire_pos, radius=0.4)
            self.fire_meshes.append(fire_mesh)
            self.plotter.add_mesh(
                fire_mesh,
                color='red',
                opacity=0.8,
                name=f'fire_{i}'
            )
        
        # Update status
        try:
            self.plotter.remove_actor('status')
        except:
            pass
        
        msg = f"Fire Simulation\nStep: {step}/{total_steps}\nFire Points: {len(self.fire_positions)}"
        self.plotter.add_text(msg, position='lower_left', font_size=12, color='yellow', name='status')
    
    def simulate_fire_expansion(self, steps: int = 30, step_delay: float = 0.3):
        """
        Simulate fire expansion through the building
        
        Args:
            steps: Number of expansion steps
            step_delay: Delay between steps in seconds
        """
        print("=" * 70)
        print("FIRE SIMULATION - MULTI-STORY BUILDING")
        print("=" * 70)
        print(f"Fire starting at: {self.fire_start}")
        print(f"Starting floor: {self.fire_start_floor + 1}")
        print(f"Expansion steps: {steps}")
        print()
        
        self.visualize_setup()
        self.plotter.show(interactive_update=True, auto_close=False)
        
        current_fire_points = [self.fire_start]
        
        for step in range(steps):
            print(f"Step {step + 1}/{steps}: Fire expanding...")
            
            # Expand fire to nearby positions
            new_fire_points = []
            expansion_radius = min(self.expansion_rate * (step + 1) * 0.15, self.max_fire_radius)
            
            for fire_point in current_fire_points:
                # Expand horizontally on same floor first
                floor_idx = int(fire_point[1] / self.agent.floor_height)
                if 0 <= floor_idx < self.agent.num_floors:
                    bounds = self.agent.floor_walk_bounds[floor_idx]
                    
                    # Expand in all horizontal directions
                    for angle in np.linspace(0, 2 * np.pi, 16):
                        x = fire_point[0] + expansion_radius * np.cos(angle)
                        z = fire_point[2] + expansion_radius * np.sin(angle)
                        y = fire_point[1]
                        
                        # Check if within building bounds
                        if (bounds['x_min'] <= x <= bounds['x_max'] and
                            bounds['z_min'] <= z <= bounds['z_max']):
                            new_point = (x, y, z)
                            # Check if not too close to existing fire
                            too_close = False
                            for existing in self.fire_positions:
                                if np.linalg.norm(np.array(new_point) - np.array(existing)) < 0.6:
                                    too_close = True
                                    break
                            if not too_close:
                                new_fire_points.append(new_point)
                                self.fire_positions.append(new_point)
                    
                    # Allow vertical expansion to adjacent floors (stairs)
                    if step > 5:  # Start vertical expansion after some horizontal spread
                        for next_floor_offset in [-1, 1]:
                            next_floor = floor_idx + next_floor_offset
                            if 0 <= next_floor < self.agent.num_floors:
                                next_bounds = self.agent.floor_walk_bounds[next_floor]
                                # Expand near stairwell area (eastern side)
                                stair_x = bounds['x_min'] + (bounds['x_max'] - bounds['x_min']) * 0.8
                                if abs(fire_point[0] - stair_x) < 2.0:  # Near stairs
                                    y = next_floor * self.agent.floor_height + 0.5
                                    x = min(max(stair_x, next_bounds['x_min']), next_bounds['x_max'])
                                    z = fire_point[2]
                                    if (next_bounds['x_min'] <= x <= next_bounds['x_max'] and
                                        next_bounds['z_min'] <= z <= next_bounds['z_max']):
                                        new_point = (x, y, z)
                                        too_close = False
                                        for existing in self.fire_positions:
                                            if np.linalg.norm(np.array(new_point) - np.array(existing)) < 1.0:
                                                too_close = True
                                                break
                                        if not too_close:
                                            new_fire_points.append(new_point)
                                            self.fire_positions.append(new_point)
            
            current_fire_points.extend(new_fire_points)
            
            # Limit total fire points
            if len(current_fire_points) > 100:
                current_fire_points = current_fire_points[:100]
            
            # Update visualization
            self.update_fire_visualization(step + 1, steps)
            self.plotter.update()
            
            print(f"  Fire points: {len(self.fire_positions)}")
            time.sleep(step_delay)
        
        # Final message
        self.plotter.add_text(
            f"Fire Simulation Complete!\nTotal Fire Points: {len(self.fire_positions)}",
            position='upper_edge',
            font_size=16,
            color='red',
            name='complete'
        )
        
        print()
        print("Fire simulation complete!")
        print(f"Total fire points: {len(self.fire_positions)}")
        print("\nClose the window to exit.")
        self.plotter.show()
    
    def cleanup(self):
        """Clean up resources"""
        if self.plotter:
            self.plotter.close()
        self.agent.cleanup()

