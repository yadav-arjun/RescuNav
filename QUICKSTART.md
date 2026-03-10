# RescuNav Rescue System - Quick Start Guide

**GitHub Repository:** [https://github.com/yadav-arjun/RescuNav](https://github.com/yadav-arjun/RescuNav)

Get started with the AI-powered emergency rescue simulation system in 5 minutes!

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_rescue.txt
```

### 2. Set Up Environment Variables

Create a `.env` file with your credentials:

```env
# MongoDB Atlas (optional - system works without it but won't save learning data)
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=building_analysis

# Fireworks AI (optional - for video-based fire analysis)
FIREWORKS_API_KEY=your_fireworks_api_key
```

Note: The system works without database/API keys, but won't persist learning data or use video analysis.

## Quick Test

### Test All Components

```bash
python tests/run_all_tests.py
```

This will verify all components are working correctly.

### Test Individual Components

```bash
# Test building navigation
python building_navigator.py

# Test danger simulation
python danger_simulator.py

# Test AI agents
python nemo_rescue_agents.py
```

## Run Your First Simulation

### Fire Scenario (5 iterations)

```bash
python rescue_simulation.py --scenario fire --iterations 5 --agents 3
```

Expected output:
- 5 rescue attempts will run
- Agents will learn from each failure
- Success rate should improve over iterations
- Final statistics will be displayed

### Attacker Scenario (run until success)

```bash
python rescue_simulation.py --scenario attacker --until-success --max-iterations 20
```

This runs attempts until one succeeds or max iterations reached.

## Understanding the Output

### During Simulation

```
======================================================================
ITERATION 3
======================================================================

Learning from 2 previous attempts
Success rate so far: 0/2

======================================================================
Starting Rescue Mission: mission_1673821456
Scenario: fire
======================================================================

Agent rescue_agent_0 planned route: 30 steps
Agent rescue_agent_1 planned route: 32 steps
Agent rescue_agent_2 planned route: 28 steps

Agent rescue_agent_0 detected high danger (0.75), replanning...
Agent rescue_agent_1 reached the child!

======================================================================
MISSION SUCCESS! Time: 42.5s
======================================================================
```

### Mission Summary

```
----------------------------------------------------------------------
ITERATION 3 SUMMARY
----------------------------------------------------------------------
Result: SUCCESS
Time: 42.5s
Agents: 3
Alive: 2
Rescued: 1

Agent Details:
  rescue_agent_0: DEAD, NO CHILD, Health: 0.00, Path: 18 steps, Danger: 9.23
  rescue_agent_1: ALIVE, HAS CHILD, Health: 0.73, Path: 32 steps, Danger: 2.71
  rescue_agent_2: ALIVE, NO CHILD, Health: 0.85, Path: 28 steps, Danger: 1.52

Learning Progress:
  Total Attempts: 3
  Successful: 1
  Success Rate: 33.3%
----------------------------------------------------------------------
```

## Common Scenarios

### 1. Fire with Video Analysis

If you have a video of fire spreading:

```bash
python rescue_simulation.py --scenario fire --video main.mp4 --iterations 10
```

The system will:
- Analyze video using Fireworks AI
- Detect fire locations and progression
- Use real fire data for simulation

### 2. Multiple Agents for Better Success

```bash
python rescue_simulation.py --scenario fire --agents 5 --iterations 10
```

More agents = higher success probability but slower execution.

### 3. View Statistics Only

```bash
python rescue_simulation.py --stats-only
```

Shows all historical mission data without running new simulations.

## What's Happening Under the Hood

### 1. Building Setup
- 4-story building with 20x20 grid per floor
- Stairwells connecting floors
- Child located on top floor (floor 3)
- Agents start on ground floor (floor 0)

### 2. Danger Simulation
- **Fire**: Starts on lower floors, spreads over time, heat rises
- **Attacker**: Patrols between floors 2-3 continuously

### 3. Agent Planning
- Agents use A* pathfinding to find routes
- Avoid high-danger areas
- Coordinate with other agents
- Learn from previous failures

### 4. Mission Execution
- Agents navigate step-by-step
- Dangers update in real-time
- Agents take damage in dangerous areas
- Dynamic replanning when needed

### 5. Learning
- Successful paths stored
- Dangerous areas identified
- Failure patterns analyzed
- Next iteration improves strategy

## Typical Learning Curve

```
Iteration 1: 0% success (no knowledge)
Iteration 2: 0% success (learning dangerous areas)
Iteration 3: 20% success (found one safe path)
Iteration 4: 40% success (refined strategies)
Iteration 5: 60% success (consistent success patterns)
Iteration 10: 80% success (optimized paths)
```

## Next Steps

### Visualize Results

After running simulations with database enabled:

```bash
# List recent missions in MongoDB
# Then visualize a specific mission:
python visualize_rescue.py mission_1673821456
```

This creates:
- 3D visualization of agent paths
- 2D floor plans
- Danger zone overlays

### Customize Parameters

Edit the configuration files:

- `building_navigator.py` - Building structure
- `danger_simulator.py` - Danger behaviors
- `nemo_rescue_agents.py` - Agent strategies

### Advanced Usage

See [README_RESCUE.md](README_RESCUE.md) for:
- Detailed architecture
- Database schema
- Component APIs
- Advanced features

## Troubleshooting

### "No module named 'networkx'"
```bash
pip install networkx numpy scipy matplotlib
```

### "No path found!"
- Dangers might be too severe
- Try increasing number of agents
- Check building configuration

### "Mission Failed: timeout"
- Increase max_time in simulation
- Reduce danger intensity
- Add more agents

### MongoDB Connection Error
- System works without MongoDB
- Learning data won't persist
- Set `MONGODB_URI` in `.env` to enable

## Performance Tips

1. **Faster Iterations**: Reduce `num_agents`
2. **Better Success**: Increase `num_agents`
3. **Quicker Learning**: Run more iterations
4. **Detailed Analysis**: Enable database + visualization

## Example Workflow

```bash
# 1. Quick test
python tests/run_all_tests.py

# 2. Run fire scenario
python rescue_simulation.py --scenario fire --iterations 10 --agents 3

# 3. Run attacker scenario
python rescue_simulation.py --scenario attacker --iterations 10 --agents 3

# 4. View combined statistics
python rescue_simulation.py --stats-only

# 5. If database enabled, visualize best mission
python visualize_rescue.py <mission_id>
```

## Getting Help

- Read detailed docs: [README_RESCUE.md](README_RESCUE.md)
- Run component tests: `python tests/run_all_tests.py`
- Check individual modules: `python <module_name>.py`

## Key Features to Try

✅ **Fire Scenario**: Dynamic fire spread with video analysis
✅ **Attacker Scenario**: Moving threat patrol
✅ **Multi-Agent Coordination**: Agents share knowledge
✅ **Iterative Learning**: Improves over time
✅ **3D Pathfinding**: A* algorithm with danger avoidance
✅ **Database Integration**: Persistent learning (optional)
✅ **Visualization**: 3D and 2D mission replays (optional)

---

**Ready to save the child? Run your first simulation now!**

```bash
python rescue_simulation.py --scenario fire --iterations 5
```
