# RescuNav: AI-Powered Emergency Rescue Simulation

**GitHub Repository:** [https://github.com/yadav-arjun/RescuNav](https://github.com/yadav-arjun/RescuNav)

An advanced emergency response simulation system using NVIDIA NeMo-based collaborative AI agents to find optimal rescue paths in dangerous building scenarios. The system learns from failures and iteratively improves rescue success rates.

## Overview

This system simulates emergency rescue scenarios where AI agents must navigate a 4-story building to rescue a child while avoiding dangers (fire or attacker). The agents use collaborative intelligence, pathfinding algorithms, and iterative learning to improve their success rate over multiple attempts.

### Key Features

- **NVIDIA NeMo-Based Agents**: Collaborative AI agents that learn and coordinate
- **3D Building Navigation**: Grid-based pathfinding with A* algorithm
- **Two Danger Scenarios**:
  - **Fire**: Dynamic fire spread simulation using Fireworks AI video analysis
  - **Attacker**: Moving threat patrolling floors 2-3
- **Iterative Learning**: Atlas MongoDB database stores failed attempts for continuous improvement
- **Real-time Visualization**: 3D and 2D path visualization with danger zones
- **Performance Metrics**: Track success rates, timing, and path efficiency

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Rescue Simulation Engine                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Video Analysis (Fireworks AI)               │  │
│  │       Analyzes fire progression from video           │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Building Navigator                      │  │
│  │     3D grid-based navigation with A* pathfinding     │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Danger Simulation System                   │  │
│  │    Fire Spread  │  Attacker Movement                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      NeMo Collaborative Agent Swarm                  │  │
│  │  Multiple agents coordinate to find rescue path      │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Atlas Learning Database                      │  │
│  │  Stores trajectories, learns from failures           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Building Navigator (`building_navigator.py`)

- **3D Grid Representation**: 4-story building with 20x20 grid per floor
- **Navigation Graph**: NetworkX graph with weighted edges
- **Pathfinding**: A* algorithm with danger-aware routing
- **Special Locations**:
  - Child position: Top floor (floor 3)
  - Start position: Ground floor (floor 0)
  - Stairwells: Central connection between floors
  - Exits: Perimeter of ground floor

### 2. Danger Simulator (`danger_simulator.py`)

#### Fire Simulator
- Integrates with Fireworks AI video analysis
- Dynamic fire spread over time
- Heat rises to upper floors
- Intensity increases with time

#### Attacker Simulator
- Patrols between floors 2 and 3
- Predictable movement pattern
- High danger radius (3 meters)
- Continuous threat

### 3. NeMo Rescue Agents (`nemo_rescue_agents.py`)

- **Individual Agents**: Each with independent planning and execution
- **Collaborative Swarm**: Agents share knowledge about dangers
- **Risk Assessment**: Dynamic danger evaluation and replanning
- **Learning Application**: Applies knowledge from previous failed attempts
- **Health System**: Agents take damage in dangerous areas

### 4. Atlas Learning Database (`atlas_learning_db.py`)

MongoDB Atlas integration for persistent learning:

- **Mission Records**: Complete mission history with outcomes
- **Trajectory Storage**: Individual agent paths and decisions
- **Learning Analytics**: Aggregated success patterns and failure reasons
- **Dangerous Areas**: Identified death zones to avoid
- **Best Practices**: Successful path strategies

### 5. Rescue Simulation Engine (`rescue_simulation.py`)

Main orchestration system:

- **Iteration Management**: Run multiple rescue attempts
- **Learning Integration**: Feed historical data to new agents
- **Performance Tracking**: Monitor success rates over time
- **Video Integration**: Optional fire analysis from video files

### 6. Visualization System (`visualize_rescue.py`)

- **3D Visualization**: Complete mission view with paths and dangers
- **2D Floor Views**: Top-down view of each floor
- **Path Analysis**: Color-coded success/failure indicators
- **Database Integration**: Load and visualize historical missions

## Installation

### Prerequisites

```bash
# Python 3.8+
python --version

# MongoDB Atlas account (free tier works)
# Fireworks AI API key (for video analysis)
```

### Install Dependencies

```bash
# Install rescue system dependencies
pip install -r requirements_rescue.txt

# Install existing dependencies
pip install -r requirements.txt  # If you have one
```

### Environment Setup

Create or update your `.env` file:

```env
# Fireworks AI API Key
FIREWORKS_API_KEY=your_fireworks_api_key_here

# MongoDB Atlas Connection
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=building_analysis
MONGODB_COLLECTION=video_analysis
```

## Usage

### Basic Usage

#### Run Fire Scenario (10 iterations)

```bash
python rescue_simulation.py --scenario fire --iterations 10 --agents 3
```

#### Run Attacker Scenario (until success)

```bash
python rescue_simulation.py --scenario attacker --until-success --max-iterations 50
```

#### Use Video Analysis for Fire

```bash
python rescue_simulation.py --scenario fire --video main.mp4 --iterations 20
```

### Command-Line Options

```bash
python rescue_simulation.py [options]

Options:
  --scenario {fire,attacker}  Rescue scenario type (default: fire)
  --video PATH               Path to video file for fire analysis
  --iterations N             Number of iterations to run (default: 10)
  --agents N                 Number of agents per iteration (default: 3)
  --until-success           Run until successful rescue
  --max-iterations N         Maximum iterations for until-success (default: 50)
  --stats-only              Only show statistics, don't run simulation
```

### View Statistics

```bash
python rescue_simulation.py --stats-only
```

### Visualize Mission

```bash
# Get mission ID from database or simulation output
python visualize_rescue.py mission_1673821456
```

## How It Works

### Mission Flow

1. **Initialization**
   - Building structure created
   - Danger scenario initialized (fire or attacker)
   - Agent swarm created with learning data from previous attempts

2. **Planning Phase**
   - Agents coordinate to plan diverse routes
   - Share knowledge about known dangerous areas
   - Calculate risk-aware paths using A*

3. **Execution Phase**
   - Agents navigate step-by-step toward child
   - Danger simulation updates (fire spreads, attacker moves)
   - Agents take damage in dangerous areas
   - Dynamic replanning when high danger detected

4. **Outcome**
   - **Success**: At least one agent reaches child alive
   - **Failure**: All agents die or timeout reached
   - Results stored in Atlas database

5. **Learning Phase**
   - Trajectories analyzed
   - Dangerous positions recorded
   - Successful strategies identified
   - Next iteration uses improved knowledge

### Learning Mechanism

The system learns through:

1. **Dangerous Area Identification**: Records where agents died
2. **Successful Path Storage**: Saves efficient successful routes
3. **Risk Tolerance Adjustment**: Modifies based on historical success
4. **Failure Pattern Analysis**: Identifies common failure reasons

Each new iteration has access to:
- All previous mission outcomes
- Best successful trajectories
- Known dangerous positions
- Average success metrics

## Data Stored in Atlas Database

### Collections

#### `rescue_missions`
- Mission metadata
- Success/failure status
- Total time taken
- Agent statistics

#### `rescue_trajectories`
- Individual agent paths
- Health and damage data
- Death positions
- Decision history

#### `rescue_learning`
- Aggregated learning data
- Success patterns
- Dangerous areas
- Best strategies

## Performance Metrics

The system tracks:

- **Success Rate**: Percentage of successful rescues
- **Average Time**: Mean time for successful rescues
- **Agent Survival**: Percentage of agents surviving
- **Path Efficiency**: Path length vs. optimal path
- **Learning Curve**: Success rate improvement over iterations

## Example Output

```
======================================================================
ITERATION 5
======================================================================

Learning from 4 previous attempts
Success rate so far: 1/4

======================================================================
Starting Rescue Mission: mission_1673821456
Scenario: fire
======================================================================

Agent rescue_agent_0 planned route: 45 steps
Agent rescue_agent_1 planned route: 47 steps
Agent rescue_agent_2 planned route: 43 steps

... [Mission execution] ...

======================================================================
MISSION SUCCESS! Time: 38.5s
======================================================================

----------------------------------------------------------------------
ITERATION 5 SUMMARY
----------------------------------------------------------------------
Result: SUCCESS
Time: 38.5s
Agents: 3
Alive: 2
Rescued: 1

Agent Details:
  rescue_agent_0: DEAD, NO CHILD, Health: 0.00, Path: 23 steps, Danger: 8.45
  rescue_agent_1: ALIVE, HAS CHILD, Health: 0.67, Path: 45 steps, Danger: 3.21
  rescue_agent_2: ALIVE, NO CHILD, Health: 0.89, Path: 41 steps, Danger: 1.12

Learning Progress:
  Total Attempts: 5
  Successful: 2
  Success Rate: 40.0%
----------------------------------------------------------------------
```

## Testing Individual Components

### Test Building Navigation

```bash
python building_navigator.py
```

### Test Danger Simulation

```bash
python danger_simulator.py
```

### Test NeMo Agents

```bash
python nemo_rescue_agents.py
```

### Test Database

```bash
python atlas_learning_db.py
```

## Advanced Features

### Custom Building Configuration

Edit `building_navigator.py` to modify:
- Number of floors
- Grid size
- Floor height
- Stairwell positions
- Child/start locations

### Custom Danger Parameters

Edit `danger_simulator.py` to adjust:
- Fire spread rate
- Fire intensity increase
- Attacker movement speed
- Danger radius

### Agent Behavior

Edit `nemo_rescue_agents.py` to tune:
- Risk tolerance
- Exploration rate
- Health damage model
- Planning algorithms

## Troubleshooting

### Common Issues

1. **MongoDB Connection Fails**
   - Verify `MONGODB_URI` in `.env`
   - Check network/firewall settings
   - Ensure IP whitelist in MongoDB Atlas

2. **Video Analysis Fails**
   - Verify `FIREWORKS_API_KEY` in `.env`
   - Check video file format (MP4 recommended)
   - Ensure video file exists at specified path

3. **Import Errors**
   - Install all dependencies: `pip install -r requirements_rescue.txt`
   - Check Python version (3.8+ required)

4. **No Successful Rescues**
   - Increase max iterations
   - Increase number of agents
   - Adjust danger parameters
   - Check if dangers are too severe

## Future Enhancements

- Real-time 3D visualization during simulation
- Multi-objective optimization (time vs. safety)
- Reinforcement learning integration
- Multi-child rescue scenarios
- Dynamic building layouts
- Real-world building model import
- Distributed agent training

## Credits

- **Building Navigation**: NetworkX, NumPy
- **AI Agents**: NVIDIA NeMo (simulated for this demo)
- **Video Analysis**: Fireworks AI
- **Database**: MongoDB Atlas
- **Visualization**: Matplotlib

## Contact

For questions or issues, please open a GitHub issue at:  
**Repository:** [https://github.com/yadav-arjun/RescuNav](https://github.com/yadav-arjun/RescuNav)
