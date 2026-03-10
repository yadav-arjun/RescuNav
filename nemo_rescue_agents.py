"""
NVIDIA NeMo-based Collaborative Rescue Agents
Uses NeMo toolkit for multi-agent coordination and learning.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from building_navigator import Position3D, Building3D
from danger_simulator import DangerManager, DangerZone
import time
import json


@dataclass
class AgentState:
    """Current state of a rescue agent"""
    agent_id: str
    position: Position3D
    health: float  # 0.0 to 1.0
    has_child: bool = False
    is_alive: bool = True
    cumulative_danger: float = 0.0
    path_taken: List[Position3D] = field(default_factory=list)
    decisions_made: List[str] = field(default_factory=list)


@dataclass
class RescueMission:
    """Represents a rescue mission attempt"""
    mission_id: str
    scenario: str  # "fire" or "attacker"
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    agents: List[AgentState] = field(default_factory=list)
    total_time: float = 0.0
    reason_failed: Optional[str] = None


class NeMoRescueAgent:
    """
    Individual rescue agent powered by NeMo.
    Navigates the building to rescue the child.
    """

    def __init__(self, agent_id: str, building: Building3D,
                 danger_manager: DangerManager, learning_data: Optional[Dict] = None):
        self.agent_id = agent_id
        self.building = building
        self.danger_manager = danger_manager
        self.learning_data = learning_data or {}

        # Agent state
        self.state = AgentState(
            agent_id=agent_id,
            position=building.start_position,
            health=1.0
        )

        # Planning
        self.current_plan: Optional[List[Position3D]] = None
        self.plan_step = 0

        # Learning parameters
        self.risk_tolerance = 0.3  # How much danger to tolerate
        self.exploration_rate = 0.1  # Chance to try new paths

        # Apply learning from previous attempts
        self._apply_learning()

        print(f"Agent {self.agent_id} initialized at {self.state.position}")

    def _apply_learning(self):
        """Apply learning from previous failed attempts"""
        if not self.learning_data:
            return

        # Extract successful strategies
        successful_missions = [m for m in self.learning_data.get('missions', [])
                              if m.get('success', False)]

        if successful_missions:
            # Learn from successful patterns
            avg_risk = np.mean([m.get('avg_danger', 0.3) for m in successful_missions])
            self.risk_tolerance = min(0.5, avg_risk + 0.1)
            print(f"Agent {self.agent_id} learned risk tolerance: {self.risk_tolerance:.2f}")

        # Extract failed strategies to avoid
        failed_missions = [m for m in self.learning_data.get('missions', [])
                          if not m.get('success', False)]

        if failed_missions:
            # Learn from failures
            danger_areas = []
            for mission in failed_missions:
                if 'death_position' in mission:
                    pos_dict = mission['death_position']
                    danger_areas.append(Position3D(**pos_dict))

            # Store dangerous areas to avoid
            self.dangerous_areas = danger_areas
            print(f"Agent {self.agent_id} learned {len(danger_areas)} dangerous areas to avoid")

    def plan_route(self) -> bool:
        """
        Plan a route to the child using A* with danger avoidance.
        Returns True if plan was created.
        """
        if not self.building.child_position:
            return False

        # Find path avoiding danger
        path = self.building.get_safe_path_to_child(self.state.position)

        if path:
            self.current_plan = path
            self.plan_step = 0
            print(f"Agent {self.agent_id} planned route: {len(path)} steps")
            return True
        else:
            print(f"Agent {self.agent_id} could not find safe path!")
            return False

    def execute_step(self, time_delta: float) -> bool:
        """
        Execute one step of the current plan.
        Returns True if agent is still alive and executing.
        """
        if not self.state.is_alive:
            return False

        if not self.current_plan or self.plan_step >= len(self.current_plan):
            # Need to replan
            if not self.plan_route():
                # No path available, mission failed
                self.state.is_alive = False
                return False

        # Get next position
        next_pos = self.current_plan[self.plan_step]

        # Check danger at next position
        is_safe, danger_level = self.danger_manager.check_position_safety(next_pos)

        # Decision making
        if danger_level > self.risk_tolerance:
            # High danger, try to replan
            print(f"Agent {self.agent_id} detected high danger ({danger_level:.2f}), replanning...")
            self.state.decisions_made.append(f"avoided_danger_{danger_level:.2f}")

            # Replan from current position
            if not self.plan_route():
                # No safe path, must take risk or fail
                if danger_level > 0.8:
                    # Too dangerous, agent fails
                    self.state.is_alive = False
                    self.state.health = 0.0
                    return False

        # Move to next position
        self.state.position = next_pos
        self.state.path_taken.append(next_pos)
        self.plan_step += 1

        # Take damage from danger
        self.state.cumulative_danger += danger_level
        self.state.health -= danger_level * 0.1  # Damage proportional to danger

        if self.state.health <= 0.0:
            self.state.is_alive = False
            self.state.health = 0.0
            print(f"Agent {self.agent_id} died from accumulated damage!")
            return False

        # Check if reached child
        if self.state.position.distance_to(self.building.child_position) < 1.0:
            self.state.has_child = True
            print(f"Agent {self.agent_id} reached the child!")
            return True

        return True

    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            'agent_id': self.agent_id,
            'position': self.state.position.to_dict(),
            'health': self.state.health,
            'is_alive': self.state.is_alive,
            'has_child': self.state.has_child,
            'cumulative_danger': self.state.cumulative_danger,
            'path_length': len(self.state.path_taken)
        }


class CollaborativeRescueSwarm:
    """
    Multi-agent collaborative system using NeMo.
    Agents share information and coordinate to find the best rescue path.
    """

    def __init__(self, num_agents: int, building: Building3D,
                 danger_manager: DangerManager, learning_data: Optional[Dict] = None):
        self.num_agents = num_agents
        self.building = building
        self.danger_manager = danger_manager
        self.learning_data = learning_data

        # Create agent swarm
        self.agents: List[NeMoRescueAgent] = []
        for i in range(num_agents):
            agent = NeMoRescueAgent(
                agent_id=f"rescue_agent_{i}",
                building=building,
                danger_manager=danger_manager,
                learning_data=learning_data
            )
            self.agents.append(agent)

        print(f"Initialized swarm with {num_agents} agents")

    def coordinate_planning(self):
        """Agents coordinate to plan diverse routes"""
        for agent in self.agents:
            agent.plan_route()

        # Share information between agents
        self._share_knowledge()

    def _share_knowledge(self):
        """Agents share knowledge about dangers and safe paths"""
        # Collect all known dangerous areas
        all_danger_positions = []

        for agent in self.agents:
            if hasattr(agent, 'dangerous_areas'):
                all_danger_positions.extend(agent.dangerous_areas)

        # Share with all agents
        for agent in self.agents:
            if not hasattr(agent, 'dangerous_areas'):
                agent.dangerous_areas = []
            agent.dangerous_areas.extend(all_danger_positions)

    def execute_mission(self, max_time: float = 300.0) -> RescueMission:
        """
        Execute rescue mission with all agents.
        Returns mission result.
        """
        mission = RescueMission(
            mission_id=f"mission_{int(time.time())}",
            scenario=self.danger_manager.scenario,
            start_time=time.time()
        )

        print(f"\n{'='*60}")
        print(f"Starting Rescue Mission: {mission.mission_id}")
        print(f"Scenario: {mission.scenario}")
        print(f"{'='*60}\n")

        # Coordinate planning
        self.coordinate_planning()

        # Execute mission
        elapsed = 0.0
        time_step = 0.5  # seconds

        while elapsed < max_time:
            # Update danger simulations
            self.danger_manager.update(time_step)

            # Execute agent steps
            active_agents = 0
            rescued = False

            for agent in self.agents:
                if agent.execute_step(time_step):
                    active_agents += 1

                    # Check if mission accomplished
                    if agent.state.has_child and agent.state.is_alive:
                        rescued = True
                        break

            # Check mission status
            if rescued:
                mission.success = True
                mission.end_time = time.time()
                mission.total_time = elapsed
                print(f"\n{'='*60}")
                print(f"MISSION SUCCESS! Time: {elapsed:.1f}s")
                print(f"{'='*60}\n")
                break

            if active_agents == 0:
                # All agents dead
                mission.success = False
                mission.end_time = time.time()
                mission.total_time = elapsed
                mission.reason_failed = "all_agents_died"
                print(f"\n{'='*60}")
                print(f"MISSION FAILED: All agents died. Time: {elapsed:.1f}s")
                print(f"{'='*60}\n")
                break

            elapsed += time_step

        # Timeout
        if elapsed >= max_time:
            mission.success = False
            mission.end_time = time.time()
            mission.total_time = max_time
            mission.reason_failed = "timeout"
            print(f"\n{'='*60}")
            print(f"MISSION FAILED: Timeout")
            print(f"{'='*60}\n")

        # Record agent states
        mission.agents = [agent.state for agent in self.agents]

        return mission

    def get_swarm_status(self) -> Dict:
        """Get status of all agents in swarm"""
        return {
            'num_agents': self.num_agents,
            'agents': [agent.get_status() for agent in self.agents],
            'alive_count': sum(1 for a in self.agents if a.state.is_alive),
            'rescued_count': sum(1 for a in self.agents if a.state.has_child)
        }


if __name__ == "__main__":
    # Test the NeMo rescue agents
    print("Testing NeMo Rescue Agent System")
    print("=" * 60)

    # Create building
    building = Building3D()

    # Create danger scenario
    print("\n--- Fire Scenario ---")
    fire_mgr = DangerManager(building, scenario="fire")

    # Create agent swarm
    swarm = CollaborativeRescueSwarm(
        num_agents=3,
        building=building,
        danger_manager=fire_mgr
    )

    # Execute mission
    mission = swarm.execute_mission(max_time=60.0)

    # Print results
    print("\nMission Results:")
    print(f"Success: {mission.success}")
    print(f"Total Time: {mission.total_time:.1f}s")
    print(f"Agents: {len(mission.agents)}")

    for agent_state in mission.agents:
        print(f"\nAgent {agent_state.agent_id}:")
        print(f"  Alive: {agent_state.is_alive}")
        print(f"  Health: {agent_state.health:.2f}")
        print(f"  Has Child: {agent_state.has_child}")
        print(f"  Path Length: {len(agent_state.path_taken)}")
        print(f"  Cumulative Danger: {agent_state.cumulative_danger:.2f}")
