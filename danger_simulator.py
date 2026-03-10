"""
Danger Simulation System
Simulates fire spread and attacker movement in the building.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from building_navigator import Position3D, Building3D
import time
import random


@dataclass
class DangerZone:
    """Represents a dangerous area in the building"""
    position: Position3D
    danger_level: float  # 0.0 to 1.0
    radius: float  # meters
    type: str  # "fire" or "attacker"
    timestamp: float


class FireSimulator:
    """
    Simulates fire spread through the building.
    Uses video analysis from Fireworks AI to determine initial fire locations.
    """

    def __init__(self, building: Building3D, video_analysis_data: Optional[dict] = None):
        self.building = building
        self.video_data = video_analysis_data
        self.fire_zones: List[DangerZone] = []
        self.spread_rate = 0.1  # meters per second
        self.intensity_increase = 0.05  # per second

        # Initialize fire from video data or random
        self._initialize_fire()

    def _initialize_fire(self):
        """Initialize fire positions based on video analysis or random placement"""
        if self.video_data and 'fire_frames' in self.video_data:
            # Use video analysis to determine fire locations
            print("Initializing fire from video analysis...")
            self._init_from_video()
        else:
            # Random fire placement for testing
            print("Initializing random fire scenario...")
            self._init_random_fire()

    def _init_from_video(self):
        """Initialize fire from video analysis data"""
        # Extract fire positions from video analysis
        # This would be integrated with the existing VideoAnalyzer
        fire_frames = self.video_data.get('fire_frames', [])

        if fire_frames:
            # Start fire on floors 0-2 based on video
            for i, frame_num in enumerate(fire_frames[:3]):
                floor = i % 3
                x = random.uniform(5.0, 15.0)
                y = random.uniform(5.0, 15.0)
                z = floor * self.building.floor_height

                pos = Position3D(x, y, z, floor)
                danger = DangerZone(
                    position=pos,
                    danger_level=0.6,
                    radius=2.0,
                    type="fire",
                    timestamp=time.time()
                )
                self.fire_zones.append(danger)

    def _init_random_fire(self):
        """Initialize random fire positions for testing"""
        # Start fires on floors 0, 1, and 2
        starting_floors = [0, 1, 2]

        for floor in starting_floors:
            x = random.uniform(5.0, 15.0)
            y = random.uniform(5.0, 15.0)
            z = floor * self.building.floor_height

            pos = Position3D(x, y, z, floor)
            danger = DangerZone(
                position=pos,
                danger_level=0.5,
                radius=2.0,
                type="fire",
                timestamp=time.time()
            )
            self.fire_zones.append(danger)

        print(f"Initialized {len(self.fire_zones)} fire zones")

    def update(self, elapsed_time: float):
        """
        Update fire spread and intensity over time.
        elapsed_time: seconds since simulation start
        """
        current_time = time.time()

        # Increase existing fire intensity and radius
        for zone in self.fire_zones:
            time_active = current_time - zone.timestamp

            # Increase danger level
            zone.danger_level = min(1.0, zone.danger_level + self.intensity_increase * elapsed_time)

            # Increase radius (fire spreads)
            zone.radius = min(5.0, zone.radius + self.spread_rate * elapsed_time)

        # Fire can spread to adjacent areas
        self._spread_fire()

        # Update building danger zones
        self._update_building_danger()

    def _spread_fire(self):
        """Fire spreads to adjacent areas"""
        new_zones = []

        for zone in self.fire_zones:
            # Fire spreads with some probability
            if zone.danger_level > 0.7 and random.random() < 0.3:
                # Spread to nearby location
                spread_x = zone.position.x + random.uniform(-3.0, 3.0)
                spread_y = zone.position.y + random.uniform(-3.0, 3.0)

                # Fire can spread upward (heat rises)
                if random.random() < 0.4 and zone.position.floor < self.building.floors - 1:
                    spread_floor = zone.position.floor + 1
                    spread_z = spread_floor * self.building.floor_height
                else:
                    spread_floor = zone.position.floor
                    spread_z = zone.position.z

                # Check bounds
                if (0 <= spread_x < self.building.grid_size * self.building.cell_size and
                    0 <= spread_y < self.building.grid_size * self.building.cell_size):

                    new_pos = Position3D(spread_x, spread_y, spread_z, spread_floor)

                    # Check if fire doesn't already exist here
                    exists = any(z.position.distance_to(new_pos) < 2.0 for z in self.fire_zones)

                    if not exists:
                        new_zone = DangerZone(
                            position=new_pos,
                            danger_level=0.4,
                            radius=1.5,
                            type="fire",
                            timestamp=time.time()
                        )
                        new_zones.append(new_zone)

        self.fire_zones.extend(new_zones)

    def _update_building_danger(self):
        """Update building's danger map with current fire positions"""
        danger_list = [(zone.position, zone.danger_level) for zone in self.fire_zones]
        self.building.update_danger_zones(danger_list)

    def get_danger_zones(self) -> List[DangerZone]:
        """Get current fire danger zones"""
        return self.fire_zones


class AttackerSimulator:
    """
    Simulates attacker movement between floors 2 and 3.
    The attacker continuously patrols this area.
    """

    def __init__(self, building: Building3D):
        self.building = building
        self.attacker_position: Position3D = None
        self.patrol_points: List[Position3D] = []
        self.current_target_idx = 0
        self.movement_speed = 1.5  # meters per second
        self.danger_radius = 3.0  # meters
        self.danger_level = 0.9  # Very dangerous

        # Initialize attacker
        self._initialize_attacker()

    def _initialize_attacker(self):
        """Initialize attacker patrol route between floors 2 and 3"""
        # Create patrol points on floors 2 and 3
        floor_2_z = 2 * self.building.floor_height
        floor_3_z = 3 * self.building.floor_height

        self.patrol_points = [
            # Floor 2 patrol
            Position3D(5.0, 5.0, floor_2_z, 2),
            Position3D(15.0, 5.0, floor_2_z, 2),
            Position3D(15.0, 15.0, floor_2_z, 2),
            Position3D(5.0, 15.0, floor_2_z, 2),

            # Move to floor 3
            Position3D(10.0, 10.0, floor_3_z, 3),  # Stairwell

            # Floor 3 patrol
            Position3D(5.0, 5.0, floor_3_z, 3),
            Position3D(15.0, 5.0, floor_3_z, 3),
            Position3D(15.0, 15.0, floor_3_z, 3),
            Position3D(5.0, 15.0, floor_3_z, 3),

            # Back to floor 2
            Position3D(10.0, 10.0, floor_2_z, 2),  # Stairwell
        ]

        self.attacker_position = self.patrol_points[0]
        print(f"Attacker initialized at {self.attacker_position}")

    def update(self, elapsed_time: float):
        """
        Update attacker position based on patrol route.
        elapsed_time: seconds since simulation start
        """
        if not self.patrol_points:
            return

        # Current target
        target = self.patrol_points[self.current_target_idx]

        # Move toward target
        distance = self.attacker_position.distance_to(target)
        move_distance = self.movement_speed * elapsed_time

        if distance <= move_distance:
            # Reached target, move to next
            self.attacker_position = target
            self.current_target_idx = (self.current_target_idx + 1) % len(self.patrol_points)
        else:
            # Move toward target
            direction = np.array([
                target.x - self.attacker_position.x,
                target.y - self.attacker_position.y,
                target.z - self.attacker_position.z
            ])
            direction = direction / np.linalg.norm(direction)
            movement = direction * move_distance

            self.attacker_position = Position3D(
                x=self.attacker_position.x + movement[0],
                y=self.attacker_position.y + movement[1],
                z=self.attacker_position.z + movement[2],
                floor=self.attacker_position.floor
            )

        # Update building danger
        self._update_building_danger()

    def _update_building_danger(self):
        """Update building's danger map with attacker position"""
        danger_list = [(self.attacker_position, self.danger_level)]
        self.building.update_danger_zones(danger_list)

    def get_danger_zones(self) -> List[DangerZone]:
        """Get current attacker danger zone"""
        return [
            DangerZone(
                position=self.attacker_position,
                danger_level=self.danger_level,
                radius=self.danger_radius,
                type="attacker",
                timestamp=time.time()
            )
        ]


class DangerManager:
    """Manages all danger simulations"""

    def __init__(self, building: Building3D, scenario: str = "fire",
                 video_data: Optional[dict] = None):
        self.building = building
        self.scenario = scenario
        self.simulators = []

        # Initialize appropriate simulator
        if scenario == "fire":
            self.fire_sim = FireSimulator(building, video_data)
            self.simulators.append(self.fire_sim)
        elif scenario == "attacker":
            self.attacker_sim = AttackerSimulator(building)
            self.simulators.append(self.attacker_sim)
        else:
            raise ValueError(f"Unknown scenario: {scenario}")

    def update(self, elapsed_time: float):
        """Update all danger simulations"""
        for sim in self.simulators:
            sim.update(elapsed_time)

    def get_all_danger_zones(self) -> List[DangerZone]:
        """Get all current danger zones"""
        zones = []
        for sim in self.simulators:
            zones.extend(sim.get_danger_zones())
        return zones

    def check_position_safety(self, position: Position3D) -> Tuple[bool, float]:
        """
        Check if a position is safe.
        Returns (is_safe, danger_level)
        """
        max_danger = 0.0

        for zone in self.get_all_danger_zones():
            distance = position.distance_to(zone.position)
            if distance <= zone.radius:
                # Danger decreases with distance
                factor = 1.0 - (distance / zone.radius)
                danger = zone.danger_level * factor
                max_danger = max(max_danger, danger)

        is_safe = max_danger < 0.3  # Threshold for safety
        return is_safe, max_danger


if __name__ == "__main__":
    # Test the danger simulators
    print("Testing Danger Simulation System")
    print("=" * 50)

    building = Building3D()

    print("\n--- Fire Scenario ---")
    fire_mgr = DangerManager(building, scenario="fire")
    print(f"Initial fire zones: {len(fire_mgr.get_all_danger_zones())}")

    # Simulate for 10 seconds
    for t in range(10):
        fire_mgr.update(1.0)
        zones = fire_mgr.get_all_danger_zones()
        print(f"Time {t+1}s: {len(zones)} danger zones")

    print("\n--- Attacker Scenario ---")
    building2 = Building3D()
    attacker_mgr = DangerManager(building2, scenario="attacker")

    # Simulate for 10 seconds
    for t in range(10):
        attacker_mgr.update(1.0)
        zones = attacker_mgr.get_all_danger_zones()
        if zones:
            pos = zones[0].position
            print(f"Time {t+1}s: Attacker at floor {pos.floor}, pos ({pos.x:.1f}, {pos.y:.1f})")
