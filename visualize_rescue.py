"""
Visualization System for Rescue Simulations
Displays agent paths, danger zones, and building structure.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import List, Dict, Optional
import json

from building_navigator import Building3D, Position3D
from danger_simulator import DangerZone
from nemo_rescue_agents import AgentState
from atlas_learning_db import AtlasLearningDatabase


class RescueVisualizer:
    """Visualize rescue simulations in 3D"""

    def __init__(self, building: Building3D):
        self.building = building

    def visualize_mission(self, agents: List[AgentState],
                         danger_zones: List[DangerZone],
                         save_path: Optional[str] = None):
        """
        Visualize a complete rescue mission.

        Args:
            agents: List of agent states with paths
            danger_zones: List of danger zones
            save_path: Optional path to save figure
        """
        fig = plt.figure(figsize=(16, 12))

        # Create 3D plot
        ax = fig.add_subplot(111, projection='3d')

        # Plot building structure
        self._plot_building(ax)

        # Plot danger zones
        self._plot_danger_zones(ax, danger_zones)

        # Plot agent paths
        self._plot_agent_paths(ax, agents)

        # Plot special positions
        self._plot_special_positions(ax)

        # Set labels and title
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.set_zlabel('Z (meters)')
        ax.set_title('Emergency Rescue Mission Visualization')

        # Add legend
        ax.legend(loc='upper right')

        # Set viewing angle
        ax.view_init(elev=20, azim=45)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")

        plt.show()

    def _plot_building(self, ax):
        """Plot building wireframe"""
        max_size = self.building.grid_size * self.building.cell_size

        # Plot floor levels
        for floor in range(self.building.floors + 1):
            z = floor * self.building.floor_height

            # Floor corners
            corners_x = [0, max_size, max_size, 0, 0]
            corners_y = [0, 0, max_size, max_size, 0]
            corners_z = [z] * 5

            ax.plot(corners_x, corners_y, corners_z, 'k-', alpha=0.3, linewidth=0.5)

        # Plot vertical edges
        for x in [0, max_size]:
            for y in [0, max_size]:
                z_line = [0, self.building.floors * self.building.floor_height]
                ax.plot([x, x], [y, y], z_line, 'k-', alpha=0.3, linewidth=0.5)

        # Plot stairwell
        stair_x = [8, 12, 12, 8, 8]
        stair_y = [8, 8, 12, 12, 8]

        for floor in range(self.building.floors):
            z = floor * self.building.floor_height
            stair_z = [z] * 5
            ax.plot(stair_x, stair_y, stair_z, 'g-', alpha=0.5, linewidth=1)

    def _plot_danger_zones(self, ax, danger_zones: List[DangerZone]):
        """Plot danger zones as colored spheres"""
        for zone in danger_zones:
            # Create sphere
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)

            x = zone.position.x + zone.radius * np.outer(np.cos(u), np.sin(v))
            y = zone.position.y + zone.radius * np.outer(np.sin(u), np.sin(v))
            z = zone.position.z + zone.radius * np.outer(np.ones(np.size(u)), np.cos(v))

            # Color based on type
            if zone.type == "fire":
                color = 'red'
                alpha = 0.3 * zone.danger_level
            else:  # attacker
                color = 'orange'
                alpha = 0.4 * zone.danger_level

            ax.plot_surface(x, y, z, color=color, alpha=alpha)

    def _plot_agent_paths(self, ax, agents: List[AgentState]):
        """Plot agent trajectories"""
        colors = ['blue', 'cyan', 'magenta', 'yellow', 'green']

        for i, agent in enumerate(agents):
            if not agent.path_taken:
                continue

            # Extract coordinates
            xs = [pos.x for pos in agent.path_taken]
            ys = [pos.y for pos in agent.path_taken]
            zs = [pos.z for pos in agent.path_taken]

            # Choose color
            color = colors[i % len(colors)]

            # Line style based on success
            if agent.has_child and agent.is_alive:
                linestyle = '-'
                linewidth = 2.5
                label = f'{agent.agent_id} (SUCCESS)'
            elif agent.is_alive:
                linestyle = '--'
                linewidth = 1.5
                label = f'{agent.agent_id} (ALIVE)'
            else:
                linestyle = ':'
                linewidth = 1.0
                label = f'{agent.agent_id} (DEAD)'

            # Plot path
            ax.plot(xs, ys, zs, color=color, linestyle=linestyle,
                   linewidth=linewidth, label=label, alpha=0.8)

            # Mark start and end
            ax.scatter(xs[0], ys[0], zs[0], color=color, marker='o',
                      s=100, edgecolors='black', alpha=1.0)

            if not agent.is_alive:
                # Mark death position with X
                ax.scatter(xs[-1], ys[-1], zs[-1], color='red', marker='x',
                          s=200, linewidths=3, alpha=1.0)
            elif agent.has_child:
                # Mark success with star
                ax.scatter(xs[-1], ys[-1], zs[-1], color='gold', marker='*',
                          s=300, edgecolors='black', alpha=1.0)

    def _plot_special_positions(self, ax):
        """Plot child position and exits"""
        # Child position
        if self.building.child_position:
            pos = self.building.child_position
            ax.scatter(pos.x, pos.y, pos.z, color='purple', marker='D',
                      s=300, edgecolors='black', linewidths=2,
                      label='Child', alpha=1.0)

        # Start position
        if self.building.start_position:
            pos = self.building.start_position
            ax.scatter(pos.x, pos.y, pos.z, color='green', marker='s',
                      s=200, edgecolors='black', linewidths=2,
                      label='Start', alpha=1.0)

    def create_2d_floor_view(self, floor: int, agents: List[AgentState],
                            danger_zones: List[DangerZone],
                            save_path: Optional[str] = None):
        """
        Create a 2D top-down view of a specific floor.

        Args:
            floor: Floor number to visualize
            agents: List of agent states
            danger_zones: List of danger zones
            save_path: Optional path to save figure
        """
        fig, ax = plt.subplots(figsize=(12, 12))

        max_size = self.building.grid_size * self.building.cell_size

        # Plot building outline
        ax.plot([0, max_size, max_size, 0, 0],
               [0, 0, max_size, max_size, 0],
               'k-', linewidth=2)

        # Plot stairwell
        ax.add_patch(plt.Rectangle((8, 8), 4, 4,
                                   facecolor='lightgreen', edgecolor='green',
                                   alpha=0.3, label='Stairwell'))

        # Plot danger zones on this floor
        for zone in danger_zones:
            if zone.position.floor == floor:
                color = 'red' if zone.type == 'fire' else 'orange'
                circle = plt.Circle((zone.position.x, zone.position.y),
                                   zone.radius, color=color,
                                   alpha=0.3 * zone.danger_level)
                ax.add_patch(circle)

        # Plot agent paths on this floor
        colors = ['blue', 'cyan', 'magenta', 'yellow', 'green']

        for i, agent in enumerate(agents):
            # Filter path for this floor
            floor_path = [pos for pos in agent.path_taken if pos.floor == floor]

            if floor_path:
                xs = [pos.x for pos in floor_path]
                ys = [pos.y for pos in floor_path]

                color = colors[i % len(colors)]
                ax.plot(xs, ys, color=color, linewidth=2,
                       label=agent.agent_id, alpha=0.7)

                # Mark positions
                ax.scatter(xs, ys, color=color, s=20, alpha=0.5)

        # Plot special positions on this floor
        if self.building.child_position and self.building.child_position.floor == floor:
            pos = self.building.child_position
            ax.scatter(pos.x, pos.y, color='purple', marker='D',
                      s=300, edgecolors='black', linewidths=2,
                      label='Child', zorder=10)

        if self.building.start_position and self.building.start_position.floor == floor:
            pos = self.building.start_position
            ax.scatter(pos.x, pos.y, color='green', marker='s',
                      s=200, edgecolors='black', linewidths=2,
                      label='Start', zorder=10)

        ax.set_xlim(0, max_size)
        ax.set_ylim(0, max_size)
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.set_title(f'Floor {floor} - Top-Down View')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Floor {floor} visualization saved to {save_path}")

        plt.show()


def visualize_from_database(mission_id: str, output_dir: str = "visualizations"):
    """
    Load mission from database and visualize it.

    Args:
        mission_id: Mission ID to visualize
        output_dir: Directory to save visualizations
    """
    import os

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load from database
    db = AtlasLearningDatabase()

    # Get mission
    mission_doc = db.missions_collection.find_one({"mission_id": mission_id})
    if not mission_doc:
        print(f"Mission {mission_id} not found!")
        return

    # Get trajectories
    trajectories = list(db.trajectories_collection.find({"mission_id": mission_id}))

    print(f"Visualizing mission: {mission_id}")
    print(f"Scenario: {mission_doc['scenario']}")
    print(f"Success: {mission_doc['success']}")
    print(f"Total Time: {mission_doc['total_time']:.1f}s")

    # Reconstruct agent states
    agents = []
    for traj in trajectories:
        # Convert path dict back to Position3D objects
        path = [Position3D(p['x'], p['y'], p['z'], p['floor'])
                for p in traj['path']]

        agent_state = AgentState(
            agent_id=traj['agent_id'],
            position=path[-1] if path else Position3D(0, 0, 0, 0),
            health=traj['final_health'],
            has_child=traj['has_child'],
            is_alive=traj['is_alive'],
            cumulative_danger=traj['cumulative_danger'],
            path_taken=path,
            decisions_made=traj.get('decisions', [])
        )
        agents.append(agent_state)

    # Create visualizer
    building = Building3D()
    visualizer = RescueVisualizer(building)

    # Note: We don't have real-time danger zones from database,
    # so we'll create placeholder ones
    danger_zones = []

    # Create 3D visualization
    save_path_3d = os.path.join(output_dir, f"{mission_id}_3d.png")
    visualizer.visualize_mission(agents, danger_zones, save_path=save_path_3d)

    # Create 2D floor views
    for floor in range(building.floors):
        save_path_2d = os.path.join(output_dir, f"{mission_id}_floor_{floor}.png")
        visualizer.create_2d_floor_view(floor, agents, danger_zones, save_path=save_path_2d)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        mission_id = sys.argv[1]
        visualize_from_database(mission_id)
    else:
        print("Usage: python visualize_rescue.py <mission_id>")
        print("\nTo get mission IDs, check the Atlas database or run:")
        print("  python rescue_simulation.py --stats-only")
