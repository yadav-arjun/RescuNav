"""
3D Building Navigation System
Provides navigation, pathfinding, and spatial representation for the 4-story building.
"""

import numpy as np
import networkx as nx
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json


class RoomType(Enum):
    HALLWAY = "hallway"
    ROOM = "room"
    STAIRWELL = "stairwell"
    EXIT = "exit"
    DANGER_ZONE = "danger_zone"


@dataclass
class Position3D:
    """3D position in the building"""
    x: float
    y: float
    z: float
    floor: int

    def distance_to(self, other: 'Position3D') -> float:
        """Calculate Euclidean distance to another position"""
        return np.sqrt(
            (self.x - other.x)**2 +
            (self.y - other.y)**2 +
            (self.z - other.z)**2
        )

    def to_dict(self) -> dict:
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'floor': self.floor
        }

    def __hash__(self):
        return hash((round(self.x, 2), round(self.y, 2), round(self.z, 2), self.floor))

    def __eq__(self, other):
        if not isinstance(other, Position3D):
            return False
        return (abs(self.x - other.x) < 0.1 and
                abs(self.y - other.y) < 0.1 and
                abs(self.z - other.z) < 0.1 and
                self.floor == other.floor)


@dataclass
class NavigationNode:
    """Node in the navigation graph"""
    position: Position3D
    room_type: RoomType
    connections: List['NavigationNode']
    danger_level: float = 0.0  # 0.0 = safe, 1.0 = deadly

    def __hash__(self):
        return hash(self.position)


class Building3D:
    """
    Represents a 4-story building with navigation capabilities.
    Simplified grid-based representation for efficient pathfinding.
    """

    def __init__(self, floors: int = 4, floor_height: float = 3.0):
        self.floors = floors
        self.floor_height = floor_height
        self.grid_size = 20  # 20x20 grid per floor
        self.cell_size = 1.0  # meters

        # Navigation graph
        self.graph = nx.Graph()
        self.nodes: Dict[Position3D, NavigationNode] = {}

        # Special positions
        self.child_position: Optional[Position3D] = None
        self.start_position: Optional[Position3D] = None
        self.exits: List[Position3D] = []

        # Initialize building structure
        self._initialize_building()

    def _initialize_building(self):
        """Create the building navigation structure"""
        print("Initializing 4-story building navigation graph...")

        # Create grid nodes for each floor
        for floor in range(self.floors):
            z = floor * self.floor_height

            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    x = i * self.cell_size
                    y = j * self.cell_size

                    pos = Position3D(x, y, z, floor)

                    # Determine room type based on position
                    room_type = self._determine_room_type(i, j, floor)

                    # Create node
                    node = NavigationNode(
                        position=pos,
                        room_type=room_type,
                        connections=[]
                    )

                    self.nodes[pos] = node
                    self.graph.add_node(pos, data=node)

        # Create connections (edges) between adjacent nodes
        self._create_connections()

        # Set special positions
        self._set_special_positions()

        print(f"Building initialized: {len(self.nodes)} nodes, {self.graph.number_of_edges()} connections")

    def _determine_room_type(self, i: int, j: int, floor: int) -> RoomType:
        """Determine room type based on grid position"""
        # Stairwells in center of building (floors 0-3)
        if 8 <= i <= 11 and 8 <= j <= 11:
            return RoomType.STAIRWELL

        # Hallways (corridors)
        if i == 10 or j == 10:
            return RoomType.HALLWAY

        # Exits on ground floor
        if floor == 0 and (i == 0 or i == self.grid_size - 1 or
                           j == 0 or j == self.grid_size - 1):
            return RoomType.EXIT

        # Regular rooms
        return RoomType.ROOM

    def _create_connections(self):
        """Create edges between adjacent navigable nodes"""
        directions = [
            (1, 0, 0),   # right
            (-1, 0, 0),  # left
            (0, 1, 0),   # forward
            (0, -1, 0),  # back
        ]

        for pos, node in self.nodes.items():
            for dx, dy, dz in directions:
                # Adjacent position
                adj_x = pos.x + dx * self.cell_size
                adj_y = pos.y + dy * self.cell_size
                adj_z = pos.z + dz
                adj_floor = pos.floor

                # Check if within bounds
                if (0 <= adj_x < self.grid_size * self.cell_size and
                    0 <= adj_y < self.grid_size * self.cell_size):

                    adj_pos = Position3D(adj_x, adj_y, adj_z, adj_floor)

                    if adj_pos in self.nodes:
                        adj_node = self.nodes[adj_pos]
                        node.connections.append(adj_node)

                        # Add edge with weight (distance)
                        weight = pos.distance_to(adj_pos)
                        self.graph.add_edge(pos, adj_pos, weight=weight)

        # Add vertical connections at stairwells
        self._add_stairwell_connections()

    def _add_stairwell_connections(self):
        """Connect floors via stairwells"""
        for floor in range(self.floors - 1):
            # Stairwell positions
            for i in range(8, 12):
                for j in range(8, 12):
                    x = i * self.cell_size
                    y = j * self.cell_size

                    pos_lower = Position3D(x, y, floor * self.floor_height, floor)
                    pos_upper = Position3D(x, y, (floor + 1) * self.floor_height, floor + 1)

                    if pos_lower in self.nodes and pos_upper in self.nodes:
                        node_lower = self.nodes[pos_lower]
                        node_upper = self.nodes[pos_upper]

                        node_lower.connections.append(node_upper)
                        node_upper.connections.append(node_lower)

                        # Vertical movement is slower
                        weight = self.floor_height * 2.0
                        self.graph.add_edge(pos_lower, pos_upper, weight=weight)

    def _set_special_positions(self):
        """Set child position, start position, and exits"""
        # Child is on the top floor (floor 3)
        self.child_position = Position3D(
            x=15.0,
            y=15.0,
            z=3 * self.floor_height,
            floor=3
        )

        # Start position on ground floor
        self.start_position = Position3D(
            x=2.0,
            y=2.0,
            z=0.0,
            floor=0
        )

        # Collect all exits
        for pos, node in self.nodes.items():
            if node.room_type == RoomType.EXIT:
                self.exits.append(pos)

    def find_path(self, start: Position3D, goal: Position3D,
                  avoid_danger: bool = True) -> Optional[List[Position3D]]:
        """
        Find optimal path from start to goal using A* algorithm.
        Optionally avoids high-danger areas.
        """
        if start not in self.nodes or goal not in self.nodes:
            return None

        try:
            # Create weight function that considers danger
            def weight_func(u, v, d):
                base_weight = d.get('weight', 1.0)

                if avoid_danger:
                    # Increase weight for dangerous areas
                    danger = self.nodes[v].danger_level
                    danger_penalty = 1.0 + (danger * 10.0)  # Up to 11x weight
                    return base_weight * danger_penalty

                return base_weight

            # A* pathfinding
            path = nx.astar_path(
                self.graph,
                start,
                goal,
                heuristic=lambda a, b: a.distance_to(b),
                weight=weight_func
            )

            return path

        except nx.NetworkXNoPath:
            return None

    def update_danger_zones(self, danger_positions: List[Tuple[Position3D, float]]):
        """
        Update danger levels for positions.
        danger_positions: List of (position, danger_level) tuples
        """
        # Reset all danger levels
        for node in self.nodes.values():
            node.danger_level = 0.0

        # Set new danger levels with area effect
        for danger_pos, danger_level in danger_positions:
            # Find nearest node
            nearest = self._find_nearest_node(danger_pos)
            if nearest:
                # Set danger with radius effect
                self._set_danger_radius(nearest, danger_level, radius=3.0)

    def _find_nearest_node(self, pos: Position3D) -> Optional[Position3D]:
        """Find the nearest navigation node to a position"""
        min_dist = float('inf')
        nearest = None

        for node_pos in self.nodes.keys():
            if node_pos.floor == pos.floor:
                dist = node_pos.distance_to(pos)
                if dist < min_dist:
                    min_dist = dist
                    nearest = node_pos

        return nearest

    def _set_danger_radius(self, center: Position3D, danger_level: float, radius: float):
        """Set danger level in a radius around a position"""
        for pos, node in self.nodes.items():
            if pos.floor == center.floor:
                dist = pos.distance_to(center)
                if dist <= radius:
                    # Danger decreases with distance
                    factor = 1.0 - (dist / radius)
                    node.danger_level = max(node.danger_level, danger_level * factor)

    def get_safe_path_to_child(self, start: Position3D) -> Optional[List[Position3D]]:
        """Get safest path from start to child position"""
        if not self.child_position:
            return None
        return self.find_path(start, self.child_position, avoid_danger=True)

    def calculate_path_danger(self, path: List[Position3D]) -> float:
        """Calculate total danger exposure along a path"""
        if not path:
            return float('inf')

        total_danger = 0.0
        for pos in path:
            if pos in self.nodes:
                total_danger += self.nodes[pos].danger_level

        return total_danger / len(path)  # Average danger

    def to_dict(self) -> dict:
        """Export building state to dictionary"""
        return {
            'floors': self.floors,
            'floor_height': self.floor_height,
            'grid_size': self.grid_size,
            'cell_size': self.cell_size,
            'child_position': self.child_position.to_dict() if self.child_position else None,
            'start_position': self.start_position.to_dict() if self.start_position else None,
            'num_nodes': len(self.nodes),
            'num_edges': self.graph.number_of_edges()
        }


if __name__ == "__main__":
    # Test the building navigation system
    print("Testing Building Navigation System")
    print("=" * 50)

    building = Building3D()

    print(f"\nBuilding Info:")
    print(json.dumps(building.to_dict(), indent=2))

    print(f"\nChild position: {building.child_position}")
    print(f"Start position: {building.start_position}")
    print(f"Number of exits: {len(building.exits)}")

    # Test pathfinding
    if building.start_position and building.child_position:
        print("\nFinding path from start to child...")
        path = building.find_path(building.start_position, building.child_position)

        if path:
            print(f"Path found! Length: {len(path)} nodes")
            print(f"Path danger: {building.calculate_path_danger(path):.3f}")
        else:
            print("No path found!")

    # Test with danger zones
    print("\nTesting with danger zones...")
    danger_zones = [
        (Position3D(10.0, 10.0, building.floor_height, 1), 0.8),  # High danger on floor 1
        (Position3D(12.0, 8.0, building.floor_height * 2, 2), 0.6),  # Medium danger on floor 2
    ]

    building.update_danger_zones(danger_zones)

    path_with_danger = building.find_path(building.start_position, building.child_position)

    if path_with_danger:
        print(f"Path with dangers: Length: {len(path_with_danger)} nodes")
        print(f"Path danger: {building.calculate_path_danger(path_with_danger):.3f}")
