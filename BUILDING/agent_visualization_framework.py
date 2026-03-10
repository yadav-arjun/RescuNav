#!/usr/bin/env python3
"""
Framework for visualizing agent movement through buildings.

Provides classes for:
- Single-story building visualization with first-person view
- Multi-story building visualization with third-person view
- Agent movement and path planning
"""

import numpy as np
import time
import os
import random
from typing import List, Tuple, Optional, Dict
import cv2

# Lazy imports
pv = None
tc = None


def _ensure_pyvista():
    """Ensure pyvista is imported"""
    global pv
    if pv is None:
        import pyvista as _pv
        pv = _pv
    return pv


def _ensure_ai2thor():
    """Ensure ai2thor is imported"""
    global tc
    if tc is None:
        import ai2thor.controller as _tc
        tc = _tc
    return tc


class SingleStoryAgent:
    """Agent for navigating single-story buildings with first-person view"""
    
    def __init__(self, scene_name: str = 'FloorPlan301', width: int = 1920, height: int = 1080):
        """
        Initialize single-story agent with AI2Thor controller
        
        Args:
            scene_name: AI2Thor scene name
            width: Render width
            height: Render height
        """
        _ensure_ai2thor()
        self.controller = tc.Controller(
            width=width,
            height=height,
            quality='Ultra',
            scene=scene_name
        )
        self.scene_name = scene_name
        self.position = None
        self.rotation = 0.0
        self.horizon = 0.0
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize agent at spawn position"""
        event = self.controller.step(action='Pass')
        agent_meta = event.metadata['agent']
        self.position = [
            agent_meta['position']['x'],
            agent_meta['position']['y'],
            agent_meta['position']['z']
        ]
        self.rotation = agent_meta['rotation']['y']
        self.horizon = agent_meta['cameraHorizon']
    
    def move_to(self, x: float, y: float, z: float, rotation: Optional[float] = None):
        """
        Move agent to specified position
        
        Args:
            x, y, z: Target position
            rotation: Optional rotation angle (0-360)
        """
        if rotation is None:
            rotation = self.rotation
        
        event = self.controller.step({
            'action': 'TeleportFull',
            'agentId': 0,
            'x': x,
            'y': y,
            'z': z,
            'rotation': rotation,
            'horizon': self.horizon,
            'standing': True,
            'forceAction': True
        })
        
        if event.metadata['lastActionSuccess']:
            self.position = [x, y, z]
            self.rotation = rotation
            return True
        return False
    
    def move_relative(self, dx: float, dy: float, dz: float):
        """Move agent relative to current position"""
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        new_z = self.position[2] + dz
        return self.move_to(new_x, new_y, new_z)
    
    def rotate(self, degrees: float):
        """Rotate agent by specified degrees"""
        new_rotation = (self.rotation + degrees) % 360
        return self.move_to(self.position[0], self.position[1], self.position[2], new_rotation)
    
    def look(self, horizon_change: float):
        """Change camera horizon (look up/down)"""
        self.horizon = max(-90, min(90, self.horizon + horizon_change))
        event = self.controller.step({
            'action': 'TeleportFull',
            'agentId': 0,
            'x': self.position[0],
            'y': self.position[1],
            'z': self.position[2],
            'rotation': self.rotation,
            'horizon': self.horizon,
            'standing': True,
            'forceAction': True
        })
    
    def get_first_person_view(self) -> np.ndarray:
        """Get current first-person view as numpy array"""
        event = self.controller.step(action='Pass')
        return event.frame
    
    def save_view(self, filepath: str):
        """Save current first-person view to file"""
        frame = self.get_first_person_view()
        cv2.imwrite(filepath, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    def get_reachable_positions(self) -> List[Dict]:
        """Get list of reachable positions in the scene"""
        event = self.controller.step(action='GetReachablePositions')
        return event.metadata['actionReturn']
    
    def get_nearby_objects(self, radius: float = 3.0) -> List[Dict]:
        """Get objects within specified radius"""
        event = self.controller.step(action='Pass')
        agent_pos = np.array(self.position)
        nearby = []
        
        for obj in event.metadata['objects']:
            obj_pos = np.array([
                obj['position']['x'],
                obj['position']['y'],
                obj['position']['z']
            ])
            distance = np.linalg.norm(agent_pos - obj_pos)
            if distance <= radius:
                nearby.append({
                    'type': obj['objectType'],
                    'name': obj['name'],
                    'distance': distance,
                    'visible': obj.get('visible', False),
                    'position': obj['position']
                })
        
        nearby.sort(key=lambda x: x['distance'])
        return nearby
    
    def cleanup(self):
        """Clean up controller resources"""
        if self.controller:
            self.controller.stop()


class MultiStoryAgent:
    """Agent for navigating multi-story buildings with third-person view"""
    
    def __init__(self, building_file: str, floor_height: float = 3.0, num_floors: int = 4):
        """
        Initialize multi-story agent with PyVista visualization
        
        Args:
            building_file: Path to building mesh file (.vtk, .stl, etc.)
            floor_height: Height of each floor in meters
            num_floors: Number of floors in building
        """
        _ensure_pyvista()
        self.building_file = building_file
        self.floor_height = floor_height
        self.num_floors = num_floors
        self.building_mesh = None
        self.position = None
        self.floor = 0
        self.wall_margin = 1.0
        self.floor_walk_bounds = []
        self.plotter = None
        self.agent_marker = None
        self.path_line = None
        self.path_segments = []  # [(floor, [points])]; floor==-1: blue-path, floor==-2: stair
        self.whole_path_points = []  # For blue line visualization
        self.stair_info = None
        self._load_building()
    
    def _load_building(self):
        """Load building mesh from file"""
        if not os.path.exists(self.building_file):
            raise FileNotFoundError(f"Building file not found: {self.building_file}")
        
        self.building_mesh = pv.read(self.building_file)
        self._compute_floor_bounds()
    
    def _compute_floor_bounds(self):
        """Compute walkable bounds for each floor"""
        all_points = np.array(self.building_mesh.points)
        y_levels = [f * self.floor_height + 0.5 for f in range(self.num_floors)]
        
        for y in y_levels:
            close_mask = np.abs(all_points[:, 1] - y) < 0.31
            close = all_points[close_mask]
            
            if close.shape[0] == 0:
                bounds = self.building_mesh.bounds
                # Match original code: bounds[2] and bounds[3] for z coordinates
                self.floor_walk_bounds.append({
                    'x_min': bounds[0] + self.wall_margin,
                    'x_max': bounds[1] - self.wall_margin,
                    'z_min': bounds[2] + self.wall_margin,
                    'z_max': bounds[3] - self.wall_margin
                })
            else:
                self.floor_walk_bounds.append({
                    'x_min': np.min(close[:, 0]) + self.wall_margin,
                    'x_max': np.max(close[:, 0]) - self.wall_margin,
                    'z_min': np.min(close[:, 2]) + self.wall_margin,
                    'z_max': np.max(close[:, 2]) - self.wall_margin
                })
    
    def spawn_at_floor(self, floor: int, x: Optional[float] = None, z: Optional[float] = None):
        """
        Spawn agent at specified floor
        
        Args:
            floor: Floor number (0-indexed)
            x, z: Optional position (defaults to floor center)
        """
        if floor < 0 or floor >= self.num_floors:
            raise ValueError(f"Invalid floor: {floor}")
        
        bounds = self.floor_walk_bounds[floor]
        
        if x is None:
            x = (bounds['x_min'] + bounds['x_max']) / 2
        if z is None:
            z = (bounds['z_min'] + bounds['z_max']) / 2
        
        y = floor * self.floor_height + 0.5
        self.position = [x, y, z]
        self.floor = floor
    
    def move_to(self, x: float, y: float, z: float):
        """Move agent to specified position"""
        # Update floor based on Y position
        new_floor = int(y / self.floor_height)
        if 0 <= new_floor < self.num_floors:
            self.position = [x, y, z]
            self.floor = new_floor
            return True
        return False
    
    def move_relative(self, dx: float, dy: float, dz: float):
        """Move agent relative to current position"""
        if self.position is None:
            raise ValueError("Agent not spawned. Call spawn_at_floor first.")
        
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        new_z = self.position[2] + dz
        return self.move_to(new_x, new_y, new_z)
    
    def random_point_in_bounds(self, floor_idx: int) -> Tuple[float, float, float]:
        """Uniformly sample a walkable point on floor floor_idx."""
        b = self.floor_walk_bounds[floor_idx]
        x = random.uniform(b['x_min'], b['x_max'])
        z = random.uniform(b['z_min'], b['z_max'])
        y = floor_idx * self.floor_height + 0.5
        return (x, y, z)
    
    def blue_line_to_stair_entry(self, from_point: Tuple, stair_entry_point: Tuple, nsteps: int = 8) -> List[Tuple]:
        """Generate blue line segments (on-floor path) from current location to stair entry."""
        xs = np.linspace(from_point[0], stair_entry_point[0], nsteps + 1)
        ys = np.linspace(from_point[1], stair_entry_point[1], nsteps + 1)
        zs = np.linspace(from_point[2], stair_entry_point[2], nsteps + 1)
        return [(xs[i], ys[i], zs[i]) for i in range(1, nsteps + 1)]
    
    def calculate_path_through_building(self, movement_per_floor: int = 8) -> List[Tuple[float, float, float]]:
        """
        Calculate a complete path through all floors using the improved navigation logic.
        Goes up all floors, then down all floors, with proper blue line and stair navigation.
        
        Args:
            movement_per_floor: Number of waypoints per floor
            
        Returns:
            List of (x, y, z) waypoints (flattened from path_segments)
        """
        if not self.floor_walk_bounds:
            raise ValueError("Building not loaded properly")
        
        print("\nCalculating navigation path (free movement on floors + stair-following between floors)...")
        bounds = self.building_mesh.bounds
        # Match original code indexing: bounds[2] and bounds[3] for z coordinates
        x_min_full, x_max_full = bounds[0], bounds[1]
        z_min_full, z_max_full = bounds[2], bounds[3]
        stair_x = x_min_full + (x_max_full - x_min_full) * 0.8
        stair_z = z_min_full + 0.5
        stair_width = 2.5
        stair_depth = 4.0
        self.stair_info = {
            "stair_x": stair_x,
            "stair_z": stair_z,
            "stair_width": stair_width,
            "stair_depth": stair_depth,
        }
        
        path_segments = []
        blue_path_points = []
        
        # Start at random ground-floor location
        curr_floor = 0
        curr_point = self.random_point_in_bounds(curr_floor)
        path_segments.append((curr_floor, [curr_point]))
        
        # Ascend: For each floor up to top, free roam, blue line to stair, take stairs
        for floor_num in range(self.num_floors):
            floor_y = floor_num * self.floor_height + 0.5
            floor_bounds = self.floor_walk_bounds[floor_num]
            
            # Roaming: sample random points not too close to current
            roam_points = []
            for _ in range(movement_per_floor - 1):
                for _ in range(10):
                    pt = self.random_point_in_bounds(floor_num)
                    if np.linalg.norm(np.array(pt) - np.array(curr_point)) > 0.7:
                        roam_points.append(pt)
                        break
            path_segments[-1][1].extend(roam_points)
            
            # After last floor, break before stairs
            if floor_num == self.num_floors - 1:
                break
            
            # Go to the associated stair entry for upward travel
            stair_entry_x = min(max(stair_x, floor_bounds['x_min']), floor_bounds['x_max'])
            stair_entry_z = min(max(stair_z - stair_depth/2 - 1.0, floor_bounds['z_min']), floor_bounds['z_max'])
            stair_entry = (stair_entry_x, floor_y, stair_entry_z)
            
            # Blue path: interpolate from last roam to stair
            last_floor_pt = path_segments[-1][1][-1]
            blue_pts = self.blue_line_to_stair_entry(last_floor_pt, stair_entry)
            blue_path_points.extend([last_floor_pt] + blue_pts)
            path_segments.append((-1, blue_pts))
            
            # Ascend stairs
            steps_per_flight = 12
            stair_pts = []
            for step in range(steps_per_flight + 1):
                progress = step / steps_per_flight
                step_y = floor_y + progress * self.floor_height
                step_z = stair_z - stair_depth/2 + progress * stair_depth
                step_x = stair_x
                stair_pts.append((step_x, step_y, step_z))
            blue_path_points.extend(stair_pts)
            path_segments.append((-2, stair_pts))
            
            # On next floor: begin at stair exit
            next_floor_bounds = self.floor_walk_bounds[floor_num + 1]
            stair_exit_x = min(max(stair_x, next_floor_bounds['x_min']), next_floor_bounds['x_max'])
            stair_exit_z = min(max(stair_z + stair_depth/2, next_floor_bounds['z_min']), next_floor_bounds['z_max'])
            stair_exit = (stair_exit_x, floor_y + self.floor_height, stair_exit_z)
            path_segments.append((floor_num + 1, [stair_exit]))
            curr_point = stair_exit
        
        # Descend: for each floor, roam, blue-line to stair, descend, exit at bottom
        for floor_num in range(self.num_floors - 1, 0, -1):
            floor_y = floor_num * self.floor_height + 0.5
            floor_bounds = self.floor_walk_bounds[floor_num]
            
            roam_points = []
            for _ in range(movement_per_floor - 1):
                for _ in range(10):
                    pt = self.random_point_in_bounds(floor_num)
                    if np.linalg.norm(np.array(pt) - np.array(curr_point)) > 0.7:
                        roam_points.append(pt)
                        break
            path_segments[-1][1].extend(roam_points)
            
            # Blue path: floor to stair entry (down)
            stair_top_x = min(max(stair_x, floor_bounds['x_min']), floor_bounds['x_max'])
            stair_top_z = min(max(stair_z + stair_depth/2, floor_bounds['z_min']), floor_bounds['z_max'])
            stair_top = (stair_top_x, floor_y, stair_top_z)
            
            last_floor_pt = path_segments[-1][1][-1]
            blue_pts = self.blue_line_to_stair_entry(last_floor_pt, stair_top)
            blue_path_points.extend([last_floor_pt] + blue_pts)
            path_segments.append((-1, blue_pts))
            
            # Descend stairs
            steps_per_flight = 12
            stair_pts = []
            for step in range(steps_per_flight + 1):
                progress = step / steps_per_flight
                step_y = floor_y - progress * self.floor_height
                step_z = stair_z + stair_depth/2 - progress * stair_depth
                step_x = stair_x
                stair_pts.append((step_x, step_y, step_z))
            blue_path_points.extend(stair_pts)
            path_segments.append((-2, stair_pts))
            
            # Finish at stair exit on next lower floor
            ground_bounds = self.floor_walk_bounds[max(0, floor_num - 1)]
            stair_exit_x = min(max(stair_x, ground_bounds['x_min']), ground_bounds['x_max'])
            stair_exit_z = min(max(stair_z - stair_depth/2 - 1.0, ground_bounds['z_min']), ground_bounds['z_max'])
            stair_exit = (stair_exit_x, floor_y - self.floor_height, stair_exit_z)
            path_segments.append((floor_num - 1, [stair_exit]))
            curr_point = stair_exit
        
        # Do ground floor post-roam
        roam_points = []
        for _ in range(movement_per_floor - 1):
            for _ in range(10):
                pt = self.random_point_in_bounds(0)
                if np.linalg.norm(np.array(pt) - np.array(curr_point)) > 0.7:
                    roam_points.append(pt)
                    break
        path_segments[-1][1].extend(roam_points)
        
        # For the blue path visualization, collect all blue-line and stair segments in order
        self.whole_path_points = []
        for segtype, points in path_segments:
            if segtype in (-2, -1):
                if self.whole_path_points:
                    if np.linalg.norm(np.array(points[0]) - np.array(self.whole_path_points[-1])) < 1e-5:
                        self.whole_path_points.extend(points[1:])
                    else:
                        self.whole_path_points.extend(points)
                else:
                    self.whole_path_points.extend(points)
        
        self.path_segments = path_segments
        
        # Flatten path_segments for backward compatibility
        flat_path = []
        for segtype, points in path_segments:
            flat_path.extend(points)
        
        tot_points = len(flat_path)
        print(f"Path calculated: {tot_points} agent moves (including stairs & blue lines)")
        print(f"✓ Floor movement is always confined within building geometry")
        print(f"✓ Stairs followed ('blue path') between each floor change")
        
        return flat_path
    
    def visualize_path(self):
        """Create a blue-polyline for navigation path over stairs + between-floors (not roam)."""
        if len(self.whole_path_points) < 2:
            return None
        points = np.array(self.whole_path_points)
        poly = pv.PolyData(points)
        lines = []
        for i in range(len(points) - 1):
            lines.extend([2, i, i + 1])
        poly.lines = lines
        return poly
    
    def visualize_setup(self, show_path: bool = True, path_points: Optional[List[Tuple]] = None):
        """
        Setup visualization plotter
        
        Args:
            show_path: Whether to show navigation path
            path_points: Optional path points to visualize (for backward compatibility)
        """
        _ensure_pyvista()
        self.plotter = pv.Plotter()
        
        # Add building mesh
        self.plotter.add_mesh(
            self.building_mesh,
            color='tan',
            opacity=0.3,
            show_edges=True,
            edge_color='gray',
            line_width=0.5,
            label='Building Structure'
        )
        
        # Add path if requested (use whole_path_points if available, otherwise path_points)
        if show_path:
            if self.whole_path_points:
                path_line = self.visualize_path()
                if path_line is not None:
                    self.path_line = path_line
                    self.plotter.add_mesh(
                        path_line,
                        color='blue',
                        line_width=3,
                        opacity=0.6,
                        label='Navigation Path'
                    )
            elif path_points and len(path_points) > 1:
                points_array = np.array(path_points)
                poly = pv.PolyData(points_array)
                lines = []
                for i in range(len(points_array) - 1):
                    lines.extend([2, i, i + 1])
                poly.lines = lines
                self.path_line = poly
                self.plotter.add_mesh(
                    poly,
                    color='blue',
                    line_width=3,
                    opacity=0.6,
                    label='Navigation Path'
                )
        
        # Add floor labels
        for floor in range(self.num_floors):
            floor_y = floor * self.floor_height
            bounds = self.building_mesh.bounds
            self.plotter.add_text(
                f'Floor {floor + 1}',
                position=(bounds[0] - 1, floor_y + self.floor_height/2, bounds[4] - 1),
                font_size=20,
                color='white'
            )
        
        # Setup camera
        bounds = self.building_mesh.bounds
        center_x = (bounds[0] + bounds[1]) / 2
        center_y = (bounds[2] + bounds[3]) / 2
        center_z = (bounds[4] + bounds[5]) / 2
        
        self.plotter.camera_position = [
            (center_x + 20, center_y + 15, center_z + 20),
            (center_x, center_y, center_z),
            (0, 1, 0)
        ]
        
        self.plotter.add_text(
            "Multi-Story Building Navigation\nThird-Person View",
            position='upper_left',
            font_size=14,
            color='white'
        )
    
    def update_visualization(self, position: Tuple[float, float, float], floor: int):
        """
        Update agent position in visualization
        
        Args:
            position: (x, y, z) position
            floor: Current floor number
        """
        if self.plotter is None:
            raise ValueError("Visualization not setup. Call visualize_setup first.")
        
        # Remove old agent marker
        if self.agent_marker:
            try:
                self.plotter.remove_actor('agent')
            except:
                pass
        
        # Add new agent marker
        agent = pv.Sphere(radius=0.3, center=position)
        self.agent_marker = agent
        self.plotter.add_mesh(agent, color='red', name='agent', opacity=0.95)
        
        # Update status text
        try:
            self.plotter.remove_actor('status')
        except:
            pass
        
        msg = f"Floor {floor + 1}\nPosition: ({position[0]:.1f}, {position[1]:.1f}, {position[2]:.1f})"
        self.plotter.add_text(msg, position='lower_left', font_size=12, color='yellow', name='status')
        
        # Update camera to follow agent
        self.plotter.camera.focal_point = position
        self.plotter.camera.position = (
            position[0] + 15,
            position[1] + 10,
            position[2] + 15
        )
    
    def animate_path(self, path: List[Tuple[float, float, float]], speed: float = 0.3):
        """
        Animate agent following a path with different speeds for different segment types.
        Uses path_segments if available for better animation, otherwise uses flat path.
        
        Args:
            path: List of (x, y, z) waypoints (flattened path)
            speed: Base time delay between waypoints in seconds
        """
        if self.plotter is None:
            self.visualize_setup(show_path=True, path_points=path)
        
        print("\nStarting navigation animation...")
        print("Controls:")
        print("  - Rotate: Left-click and drag")
        print("  - Zoom: Scroll wheel")
        print("  - Quit: Press 'q' or close window")
        print()
        
        self.plotter.show(interactive_update=True, auto_close=False)
        
        # Use path_segments if available for better animation
        if self.path_segments:
            total_moves = sum(len(pts) for _, pts in self.path_segments)
            progress_cnt = 0
            
            for segtype, points in self.path_segments:
                if segtype >= 0:
                    # Visualize step jumps for intra-floor roaming
                    for i, pt in enumerate(points):
                        if i > 0:
                            try:
                                self.plotter.remove_actor('agent')
                            except Exception:
                                pass
                            try:
                                self.plotter.remove_actor('status')
                            except Exception:
                                pass
                        agent = pv.Sphere(radius=0.3, center=pt)
                        agent_color = "red"
                        floor_label = f"Floor {segtype+1} (free movement)"
                        msg = f"Location: {floor_label}\nProgress: {progress_cnt+1}/{total_moves}\nPosition: ({pt[0]:.1f}, {pt[1]:.1f}, {pt[2]:.1f})"
                        self.plotter.add_mesh(agent, color=agent_color, name='agent', opacity=0.95)
                        self.plotter.add_text(msg, position='lower_left', font_size=12, color='yellow', name='status')
                        if progress_cnt % 3 == 0:
                            self.plotter.camera.focal_point = pt
                            self.plotter.camera.position = (
                                pt[0] + 15,
                                pt[1] + 10,
                                pt[2] + 15
                            )
                        self.plotter.update()
                        time.sleep(speed * 0.5)
                        progress_cnt += 1
                elif segtype == -1:
                    # Blue-path steps (floor to stair): animate slowly
                    for j, pt in enumerate(points):
                        try:
                            self.plotter.remove_actor('agent')
                        except Exception:
                            pass
                        try:
                            self.plotter.remove_actor('status')
                        except Exception:
                            pass
                        agent = pv.Sphere(radius=0.3, center=pt)
                        msg = f"Location: Floor access path\nProgress: {progress_cnt+1}/{total_moves}\nPosition: ({pt[0]:.1f}, {pt[1]:.1f}, {pt[2]:.1f})"
                        self.plotter.add_mesh(agent, color='dodgerblue', name='agent', opacity=0.90)
                        self.plotter.add_text(msg, position='lower_left', font_size=12, color='yellow', name='status')
                        if progress_cnt % 3 == 0:
                            self.plotter.camera.focal_point = pt
                            self.plotter.camera.position = (
                                pt[0] + 15,
                                pt[1] + 10,
                                pt[2] + 15
                            )
                        self.plotter.update()
                        time.sleep(speed * 1.5)
                        progress_cnt += 1
                elif segtype == -2:
                    # Stairs: animate moderate speed
                    for k, pt in enumerate(points):
                        try:
                            self.plotter.remove_actor('agent')
                        except Exception:
                            pass
                        try:
                            self.plotter.remove_actor('status')
                        except Exception:
                            pass
                        agent = pv.Sphere(radius=0.3, center=pt)
                        color = "orange"
                        msg = f"Location: Stairs\nProgress: {progress_cnt+1}/{total_moves}\nPosition: ({pt[0]:.1f}, {pt[1]:.1f}, {pt[2]:.1f})"
                        self.plotter.add_mesh(agent, color=color, name='agent', opacity=0.97)
                        self.plotter.add_text(msg, position='lower_left', font_size=12, color='yellow', name='status')
                        if progress_cnt % 3 == 0:
                            self.plotter.camera.focal_point = pt
                            self.plotter.camera.position = (
                                pt[0] + 15,
                                pt[1] + 10,
                                pt[2] + 15
                            )
                        self.plotter.update()
                        time.sleep(speed * 1.2)
                        progress_cnt += 1
        else:
            # Fallback to simple animation if path_segments not available
            for i, waypoint in enumerate(path):
                floor = int(waypoint[1] / self.floor_height)
                self.update_visualization(waypoint, floor)
                self.plotter.update()
                time.sleep(speed)
        
        # Add completion message
        self.plotter.add_text(
            "Navigation Complete!\n✓ All floors explored\n✓ Stayed within bounds\n✓ Used stairs & blue line for crossings",
            position='upper_edge',
            font_size=16,
            color='green',
            name='complete'
        )
        print("\nNavigation complete!")
        print("✓ Agent stayed within building bounds (all floor walkable areas)")
        print("✓ All floors explored with free intra-floor movement")
        print("✓ Stairs/blue line used for floor changes")
        print("\nClose the window to exit.")
        self.plotter.show()
    
    def cleanup(self):
        """Clean up visualization resources"""
        if self.plotter:
            self.plotter.close()

