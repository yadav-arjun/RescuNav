import ai2thor.controller as tc
import pyvista as pv
import numpy as np
import json

def get_scene_bounds(controller, scene_name='FloorPlan301'):
    """Get the bounds of the AI2Thor scene"""
    event = controller.step(dict(
        action='Initialize',
        gridSize=0.25,
        agentCount=1,
        scene=scene_name
    ))

    # Get reachable positions to determine floor bounds
    event = controller.step(action='GetReachablePositions')
    reachable_positions = event.metadata['actionReturn']

    if not reachable_positions:
        return None

    positions = np.array([[p['x'], p['y'], p['z']] for p in reachable_positions])

    bounds = {
        'x_min': positions[:, 0].min(),
        'x_max': positions[:, 0].max(),
        'y_min': positions[:, 1].min(),
        'y_max': positions[:, 1].max(),
        'z_min': positions[:, 2].min(),
        'z_max': positions[:, 2].max(),
    }

    return bounds, reachable_positions


def create_floor_from_bounds(bounds, floor_height=3.0, wall_thickness=0.3):
    """Create a floor mesh from scene bounds"""
    x_size = bounds['x_max'] - bounds['x_min']
    z_size = bounds['z_max'] - bounds['z_min']
    x_center = (bounds['x_max'] + bounds['x_min']) / 2
    z_center = (bounds['z_max'] + bounds['z_min']) / 2

    meshes = []

    # Floor slab
    floor_slab = pv.Cube(
        center=(x_center, 0, z_center),
        x_length=x_size + wall_thickness * 2,
        y_length=0.2,
        z_length=z_size + wall_thickness * 2
    )
    meshes.append(('floor', floor_slab))

    # Ceiling slab
    ceiling_slab = pv.Cube(
        center=(x_center, floor_height - 0.1, z_center),
        x_length=x_size + wall_thickness * 2,
        y_length=0.2,
        z_length=z_size + wall_thickness * 2
    )
    meshes.append(('ceiling', ceiling_slab))

    # Walls
    # Front wall (z_min)
    front_wall = pv.Cube(
        center=(x_center, floor_height/2, bounds['z_min'] - wall_thickness/2),
        x_length=x_size + wall_thickness * 2,
        y_length=floor_height,
        z_length=wall_thickness
    )
    meshes.append(('wall_front', front_wall))

    # Back wall (z_max)
    back_wall = pv.Cube(
        center=(x_center, floor_height/2, bounds['z_max'] + wall_thickness/2),
        x_length=x_size + wall_thickness * 2,
        y_length=floor_height,
        z_length=wall_thickness
    )
    meshes.append(('wall_back', back_wall))

    # Left wall (x_min)
    left_wall = pv.Cube(
        center=(bounds['x_min'] - wall_thickness/2, floor_height/2, z_center),
        x_length=wall_thickness,
        y_length=floor_height,
        z_length=z_size
    )
    meshes.append(('wall_left', left_wall))

    # Right wall (x_max)
    right_wall = pv.Cube(
        center=(bounds['x_max'] + wall_thickness/2, floor_height/2, z_center),
        x_length=wall_thickness,
        y_length=floor_height,
        z_length=z_size
    )
    meshes.append(('wall_right', right_wall))

    return meshes, (x_size, z_size, x_center, z_center)


def create_interior_walls_from_objects(controller, floor_height=3.0, wall_thickness=0.2):
    """Create interior walls based on objects in the scene"""
    event = controller.step(action='Pass')

    interior_walls = []
    objects = event.metadata['objects']

    # Find wall-like objects
    for obj in objects:
        if 'Wall' in obj['objectType'] or obj['objectType'] in ['Door', 'Doorway']:
            pos = obj['position']
            rot = obj['rotation']
            bbox = obj.get('axisAlignedBoundingBox', None)

            if bbox:
                # Create wall segment based on bounding box
                corners = bbox['cornerPoints']
                # Simplified: create a box between corner points
                # This is approximate and may need refinement

    return interior_walls


def add_windows_to_walls(wall_meshes, floor_height=3.0, window_spacing=2.5):
    """Add windows to exterior walls"""
    windows = []

    for wall_name, wall in wall_meshes:
        if 'wall_' in wall_name:
            bounds = wall.bounds
            center = wall.center

            # Determine wall orientation
            x_extent = bounds[1] - bounds[0]
            z_extent = bounds[5] - bounds[4]

            if x_extent > z_extent:  # Horizontal wall (front/back)
                num_windows = int(x_extent / window_spacing)
                for i in range(num_windows):
                    x_pos = bounds[0] + (i + 1) * x_extent / (num_windows + 1)
                    window = pv.Cube(
                        center=(x_pos, floor_height * 0.5, center[2]),
                        x_length=1.2,
                        y_length=1.5,
                        z_length=0.4
                    )
                    windows.append(window)
            else:  # Vertical wall (left/right)
                num_windows = int(z_extent / window_spacing)
                for i in range(num_windows):
                    z_pos = bounds[4] + (i + 1) * z_extent / (num_windows + 1)
                    window = pv.Cube(
                        center=(center[0], floor_height * 0.5, z_pos),
                        x_length=0.4,
                        y_length=1.5,
                        z_length=1.2
                    )
                    windows.append(window)

    return windows


def create_connecting_stairwell(num_floors, floor_height, entry_x, entry_z, stair_width=2.5, stair_depth=4.0):
    """Create stairwell that connects entries of all floors"""
    total_height = num_floors * floor_height

    components = {
        'shaft_walls': [],
        'stairs': [],
        'landings': []
    }

    # Stairwell walls
    # Front wall
    front_wall = pv.Cube(
        center=(entry_x, total_height/2, entry_z - stair_depth/2 - 0.15),
        x_length=stair_width,
        y_length=total_height,
        z_length=0.3
    )
    components['shaft_walls'].append(front_wall)

    # Back wall
    back_wall = pv.Cube(
        center=(entry_x, total_height/2, entry_z + stair_depth/2 + 0.15),
        x_length=stair_width,
        y_length=total_height,
        z_length=0.3
    )
    components['shaft_walls'].append(back_wall)

    # Side walls
    left_wall = pv.Cube(
        center=(entry_x - stair_width/2 - 0.15, total_height/2, entry_z),
        x_length=0.3,
        y_length=total_height,
        z_length=stair_depth
    )
    components['shaft_walls'].append(left_wall)

    right_wall = pv.Cube(
        center=(entry_x + stair_width/2 + 0.15, total_height/2, entry_z),
        x_length=0.3,
        y_length=total_height,
        z_length=stair_depth
    )
    components['shaft_walls'].append(right_wall)

    # Create stairs between floors
    steps_per_flight = 12
    step_rise = floor_height / steps_per_flight
    step_run = stair_depth / steps_per_flight

    for floor in range(num_floors - 1):
        base_y = floor * floor_height

        # Landing at floor level
        landing = pv.Cube(
            center=(entry_x, base_y + 0.05, entry_z - stair_depth/2 + 0.5),
            x_length=stair_width - 0.3,
            y_length=0.1,
            z_length=1.0
        )
        components['landings'].append(landing)

        # Steps going up
        for step in range(steps_per_flight):
            step_y = base_y + step * step_rise
            step_z = entry_z - stair_depth/2 + 0.5 + step * step_run

            stair_step = pv.Cube(
                center=(entry_x, step_y + step_rise/2, step_z),
                x_length=stair_width - 0.4,
                y_length=step_rise,
                z_length=step_run * 1.1
            )
            components['stairs'].append(stair_step)

    # Top floor landing
    top_landing = pv.Cube(
        center=(entry_x, (num_floors - 1) * floor_height + 0.05, entry_z + stair_depth/2 - 0.5),
        x_length=stair_width - 0.3,
        y_length=0.1,
        z_length=1.0
    )
    components['landings'].append(top_landing)

    return components


def create_4story_building_from_ai2thor():
    """Create 4-story building using AI2Thor scene data"""
    print("Initializing AI2Thor controller...")

    controller = tc.Controller(
        width=800,
        height=600,
        quality='Ultra'
    )

    scene_name = 'FloorPlan301'
    print(f"Analyzing {scene_name}...")

    # Get scene bounds
    bounds, reachable_positions = get_scene_bounds(controller, scene_name)

    if not bounds:
        print("Could not determine scene bounds. Using default dimensions.")
        bounds = {
            'x_min': -5, 'x_max': 5,
            'y_min': 0, 'y_max': 3,
            'z_min': -5, 'z_max': 5
        }

    print(f"Scene bounds: {bounds}")

    # Parameters
    num_floors = 4
    floor_height = bounds['y_max'] - bounds['y_min']
    if floor_height < 2.0 or floor_height > 4.0:
        floor_height = 3.0

    print(f"Floor height: {floor_height}m")
    print(f"Creating {num_floors} floors...")

    # Create plotter
    plotter = pv.Plotter()
    plotter.add_text(
        f"4-Story {scene_name} Building",
        position='upper_left',
        font_size=14,
        color='white'
    )

    # Create each floor
    all_meshes = []

    for floor_num in range(num_floors):
        print(f"  Building floor {floor_num + 1}...")

        # Create floor structure
        floor_meshes, (x_size, z_size, x_center, z_center) = create_floor_from_bounds(
            bounds, floor_height
        )

        # Translate to correct height
        y_offset = floor_num * floor_height

        for mesh_name, mesh in floor_meshes:
            translated_mesh = mesh.translate([0, y_offset, 0])
            all_meshes.append((f"floor{floor_num}_{mesh_name}", translated_mesh))

            # Add to visualization
            if 'floor' in mesh_name or 'ceiling' in mesh_name:
                plotter.add_mesh(translated_mesh, color='gray', opacity=0.6)
            else:  # walls
                plotter.add_mesh(translated_mesh, color='tan', opacity=0.7)

        # Add windows
        windows = add_windows_to_walls(floor_meshes, floor_height)
        for window in windows:
            translated_window = window.translate([0, y_offset, 0])
            all_meshes.append((f"floor{floor_num}_window", translated_window))
            plotter.add_mesh(translated_window, color='lightblue', opacity=0.5)

    # Create connecting stairwell at the entry point
    entry_x = bounds['x_min'] + (bounds['x_max'] - bounds['x_min']) * 0.8
    entry_z = bounds['z_min'] + 0.5

    print("Creating connecting stairwell...")
    stairwell = create_connecting_stairwell(
        num_floors, floor_height, entry_x, entry_z
    )

    # Add stairwell components
    for wall in stairwell['shaft_walls']:
        all_meshes.append(('stairwell_wall', wall))
        plotter.add_mesh(wall, color='darkgray', opacity=0.8)

    for landing in stairwell['landings']:
        all_meshes.append(('stairwell_landing', landing))
        plotter.add_mesh(landing, color='dimgray', opacity=0.9)

    for stair in stairwell['stairs']:
        all_meshes.append(('stairwell_stair', stair))
        plotter.add_mesh(stair, color='gray', opacity=0.9)

    # Combine all into unified building
    print("\nCombining all components into unified building mesh...")
    combined_building = all_meshes[0][1]

    for name, mesh in all_meshes[1:]:
        combined_building = combined_building + mesh

    # Save outputs
    print("Saving building files...")
    combined_building.save('ai2thor_4story_building.vtk')
    combined_building.save('ai2thor_4story_building.stl')
    combined_building.save('ai2thor_4story_building.ply')

    print(f"\nBuilding statistics:")
    print(f"  Total components: {len(all_meshes)}")
    print(f"  Total vertices: {combined_building.n_points:,}")
    print(f"  Total faces: {combined_building.n_cells:,}")
    print(f"  Building height: {num_floors * floor_height}m")
    print(f"  Footprint: {x_size:.1f}m x {z_size:.1f}m")

    # Configure and show visualization
    plotter.add_axes()
    plotter.show_grid()

    # Setup camera for proper building orientation (floor 0 at bottom, top floor at top)
    bounds = combined_building.bounds
    center_x = (bounds[0] + bounds[1]) / 2
    center_y = (bounds[2] + bounds[3]) / 2
    center_z = (bounds[4] + bounds[5]) / 2

    # Position camera to look at building from an angle, with Y-axis pointing up
    plotter.camera_position = [
        (center_x + 25, center_y + 18, center_z + 25),  # Camera position
        (center_x, center_y, center_z),  # Focal point
        (0, 1, 0)  # Up vector (Y-axis points up)
    ]

    print("\nDisplaying building visualization...")
    plotter.show()

    # Cleanup
    controller.stop()

    return combined_building


if __name__ == "__main__":
    print("=" * 60)
    print("4-Story Building Generator with AI2Thor Integration")
    print("=" * 60)

    building = create_4story_building_from_ai2thor()

    print("\n" + "=" * 60)
    print("Building generation complete!")
    print("Files saved:")
    print("  - ai2thor_4story_building.vtk")
    print("  - ai2thor_4story_building.stl")
    print("  - ai2thor_4story_building.ply")
    print("=" * 60)
