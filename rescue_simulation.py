"""
Main Rescue Simulation Engine
Orchestrates iterative rescue simulations with learning.
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional
from dotenv import load_dotenv

from building_navigator import Building3D, Position3D
from danger_simulator import DangerManager
from nemo_rescue_agents import CollaborativeRescueSwarm, RescueMission
from atlas_learning_db import AtlasLearningDatabase

# Optional video analysis import
try:
    from main import VideoAnalyzer
    VIDEO_ANALYSIS_AVAILABLE = True
except ImportError:
    VIDEO_ANALYSIS_AVAILABLE = False
    VideoAnalyzer = None


load_dotenv()


class RescueSimulationEngine:
    """
    Main simulation engine that runs iterative rescue attempts
    with learning from failures.
    """

    def __init__(self, scenario: str = "fire", video_path: Optional[str] = None):
        """
        Initialize simulation engine.

        Args:
            scenario: "fire" or "attacker"
            video_path: Optional path to video for fire analysis
        """
        self.scenario = scenario
        self.video_path = video_path

        print(f"\n{'='*70}")
        print(f"RESCUE SIMULATION ENGINE")
        print(f"Scenario: {scenario.upper()}")
        print(f"{'='*70}\n")

        # Initialize components
        self.building = Building3D()

        # Initialize database (optional)
        try:
            self.database = AtlasLearningDatabase()
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to database: {e}")
            print("   Simulation will run without learning persistence.\n")
            self.database = None

        # Video analysis data (if fire scenario)
        self.video_data = None
        if scenario == "fire" and video_path:
            self._analyze_video()

        # Initialize danger manager
        self.danger_manager = DangerManager(
            self.building,
            scenario=scenario,
            video_data=self.video_data
        )

        # Simulation state
        self.iteration = 0
        self.missions: List[RescueMission] = []

        print("Simulation engine initialized\n")

    def _analyze_video(self):
        """Analyze video to extract fire data"""
        if not VIDEO_ANALYSIS_AVAILABLE:
            print("⚠️  Video analysis not available (opencv not installed)")
            print("   Install with: pip install opencv-python")
            print("   Using random fire placement\n")
            return

        if not self.video_path or not os.path.exists(self.video_path):
            print("No video file found, using random fire placement")
            return

        print(f"Analyzing video: {self.video_path}")
        print("This may take a few minutes...\n")

        try:
            analyzer = VideoAnalyzer()
            video_id = analyzer.analyze_video(self.video_path, frame_skip=30)

            # Get threat summary
            threat_summary = analyzer.get_threat_summary(video_id)
            self.video_data = threat_summary

            print("\nVideo analysis complete!")
            print(f"Fire incidents detected: {threat_summary.get('fire_incidents', 0)}")

        except Exception as e:
            print(f"Video analysis failed: {e}")
            print("Continuing with random fire placement\n")

    def run_iteration(self, num_agents: int = 3) -> RescueMission:
        """
        Run one iteration of the rescue simulation.

        Args:
            num_agents: Number of agents in the swarm

        Returns:
            RescueMission result
        """
        self.iteration += 1

        print(f"\n{'='*70}")
        print(f"ITERATION {self.iteration}")
        print(f"{'='*70}\n")

        # Get learning data from previous attempts
        if self.database:
            learning_data = self.database.get_learning_data(self.scenario)
        else:
            learning_data = {'total_attempts': 0, 'missions': []}

        total_attempts = learning_data.get('total_attempts', 0)
        successful_attempts = learning_data.get('successful_attempts', 0)

        print(f"Learning from {total_attempts} previous attempts")
        if total_attempts > 0:
            print(f"Success rate so far: {successful_attempts}/{total_attempts}")

        # Create new building and danger manager for this iteration
        building = Building3D()
        danger_manager = DangerManager(
            building,
            scenario=self.scenario,
            video_data=self.video_data
        )

        # Create agent swarm with learning data
        swarm = CollaborativeRescueSwarm(
            num_agents=num_agents,
            building=building,
            danger_manager=danger_manager,
            learning_data=learning_data
        )

        # Execute mission
        mission = swarm.execute_mission(max_time=120.0)

        # Store results in database
        try:
            self.database.store_mission(mission)
        except Exception as e:
            print(f"⚠️  Warning: Failed to store mission in database: {e}")
            print("   Simulation will continue without database persistence.\n")

        # Add to local history
        self.missions.append(mission)

        # Print iteration summary
        self._print_iteration_summary(mission, learning_data)

        return mission

    def _print_iteration_summary(self, mission: RescueMission, learning_data: Dict):
        """Print summary of iteration results"""
        print(f"\n{'-'*70}")
        print(f"ITERATION {self.iteration} SUMMARY")
        print(f"{'-'*70}")

        print(f"Result: {'SUCCESS' if mission.success else 'FAILED'}")
        print(f"Time: {mission.total_time:.1f}s")
        print(f"Agents: {len(mission.agents)}")
        print(f"Alive: {sum(1 for a in mission.agents if a.is_alive)}")
        print(f"Rescued: {sum(1 for a in mission.agents if a.has_child)}")

        if not mission.success:
            print(f"Failure Reason: {mission.reason_failed}")

        # Agent details
        print(f"\nAgent Details:")
        for agent_state in mission.agents:
            status = "ALIVE" if agent_state.is_alive else "DEAD"
            child = "HAS CHILD" if agent_state.has_child else "NO CHILD"
            print(f"  {agent_state.agent_id}: {status}, {child}, "
                  f"Health: {agent_state.health:.2f}, "
                  f"Path: {len(agent_state.path_taken)} steps, "
                  f"Danger: {agent_state.cumulative_danger:.2f}")

        # Learning progress
        print(f"\nLearning Progress:")
        total = learning_data.get('total_attempts', 0) + 1
        successful = learning_data.get('successful_attempts', 0) + (1 if mission.success else 0)
        success_rate = (successful / total) * 100 if total > 0 else 0.0

        print(f"  Total Attempts: {total}")
        print(f"  Successful: {successful}")
        print(f"  Success Rate: {success_rate:.1f}%")

        print(f"{'-'*70}\n")

    def run_until_success(self, max_iterations: int = 50, num_agents: int = 3) -> bool:
        """
        Run iterations until successful rescue or max iterations reached.

        Args:
            max_iterations: Maximum number of iterations
            num_agents: Number of agents per iteration

        Returns:
            True if rescue was successful
        """
        print(f"\n{'='*70}")
        print(f"RUNNING UNTIL SUCCESS (Max {max_iterations} iterations)")
        print(f"{'='*70}\n")

        for i in range(max_iterations):
            mission = self.run_iteration(num_agents=num_agents)

            if mission.success:
                print(f"\n{'='*70}")
                print(f"RESCUE SUCCESSFUL AFTER {self.iteration} ITERATIONS!")
                print(f"{'='*70}\n")
                return True

            # Brief pause between iterations
            time.sleep(1)

        print(f"\n{'='*70}")
        print(f"MAX ITERATIONS REACHED - NO SUCCESSFUL RESCUE")
        print(f"{'='*70}\n")
        return False

    def run_multiple_iterations(self, num_iterations: int = 10, num_agents: int = 3):
        """
        Run multiple iterations to collect learning data.

        Args:
            num_iterations: Number of iterations to run
            num_agents: Number of agents per iteration
        """
        print(f"\n{'='*70}")
        print(f"RUNNING {num_iterations} ITERATIONS")
        print(f"{'='*70}\n")

        successes = 0

        for i in range(num_iterations):
            mission = self.run_iteration(num_agents=num_agents)

            if mission.success:
                successes += 1

            # Brief pause
            time.sleep(0.5)

        # Final statistics
        self._print_final_statistics(successes, num_iterations)

    def _print_final_statistics(self, successes: int, total: int):
        """Print final simulation statistics"""
        print(f"\n{'='*70}")
        print(f"SIMULATION COMPLETE")
        print(f"{'='*70}\n")

        print(f"Total Iterations: {total}")
        print(f"Successful Rescues: {successes}")
        print(f"Failed Attempts: {total - successes}")
        print(f"Success Rate: {(successes/total)*100:.1f}%")

        # Get database statistics (if available)
        if self.database:
            try:
                stats = self.database.get_mission_statistics(self.scenario)

                print(f"\nOverall Database Statistics:")
                print(f"  Total Missions: {stats['total_missions']}")
                print(f"  Success Rate: {stats['success_rate']}%")
                if stats.get('avg_time', 0) > 0:
                    print(f"  Average Success Time: {stats['avg_time']:.1f}s")
                    print(f"  Best Time: {stats['min_time']:.1f}s")
                    print(f"  Worst Time: {stats['max_time']:.1f}s")
            except Exception as e:
                print(f"\n⚠️  Could not retrieve database statistics: {e}")

        print(f"\n{'='*70}\n")

    def get_best_trajectory(self) -> Optional[Dict]:
        """Get the best successful trajectory from learning data"""
        if not self.database:
            return None

        learning_data = self.database.get_learning_data(self.scenario)

        best_trajectories = learning_data.get('best_trajectories', [])
        if not best_trajectories:
            return None

        # Return trajectory with lowest danger
        best = min(best_trajectories, key=lambda x: x.get('danger', float('inf')))
        return best


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Emergency Rescue Simulation with AI Agents")

    parser.add_argument('--scenario', type=str, choices=['fire', 'attacker'], default='fire',
                       help='Rescue scenario type')
    parser.add_argument('--video', type=str, help='Path to video file for fire analysis')
    parser.add_argument('--iterations', type=int, default=10,
                       help='Number of iterations to run')
    parser.add_argument('--agents', type=int, default=3,
                       help='Number of agents per iteration')
    parser.add_argument('--until-success', action='store_true',
                       help='Run until successful rescue')
    parser.add_argument('--max-iterations', type=int, default=50,
                       help='Maximum iterations for until-success mode')
    parser.add_argument('--stats-only', action='store_true',
                       help='Only show statistics, do not run simulation')

    args = parser.parse_args()

    # Show statistics only
    if args.stats_only:
        db = AtlasLearningDatabase()
        stats_fire = db.get_mission_statistics('fire')
        stats_attacker = db.get_mission_statistics('attacker')

        print(f"\n{'='*70}")
        print(f"RESCUE SIMULATION STATISTICS")
        print(f"{'='*70}\n")

        print("FIRE SCENARIO:")
        print(json.dumps(stats_fire, indent=2))

        print("\nATTACKER SCENARIO:")
        print(json.dumps(stats_attacker, indent=2))

        return

    # Initialize simulation
    sim = RescueSimulationEngine(
        scenario=args.scenario,
        video_path=args.video
    )

    # Run simulation
    if args.until_success:
        sim.run_until_success(
            max_iterations=args.max_iterations,
            num_agents=args.agents
        )
    else:
        sim.run_multiple_iterations(
            num_iterations=args.iterations,
            num_agents=args.agents
        )

    # Show best trajectory
    best = sim.get_best_trajectory()
    if best:
        print(f"Best Trajectory Found:")
        print(f"  Agent: {best['agent_id']}")
        print(f"  Path Length: {len(best['path'])} steps")
        print(f"  Cumulative Danger: {best['danger']:.2f}")


if __name__ == "__main__":
    main()
