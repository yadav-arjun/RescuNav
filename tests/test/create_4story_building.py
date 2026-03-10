import ai2thor.controller as tc
import pyvista as pv
import numpy as np
import trimesh

def extract_scene_mesh(controller, scene_name='FloorPlan301'):
    """Extract mesh data from AI2Thor scene"""
    print(f"Initializing {scene_name}...")
    event = controller.step(dict(
        action='Initialize',
        gridSize=0.25,
        agentCount=1,
        scene=scene_name
    ))

    # Get all object meshes from the scene
    all_meshes = []

    # Try to get mesh data from objects
    for obj in event.metadata['objects']:
        if 'mesh' in obj:
            vertices = obj['mesh']['vertices']
            faces = obj['mesh']['triangles']

            # Convert to numpy arrays
            vertices = np.array(vertices).reshape(-1, 3)
            faces = np.array(faces).reshape(-1, 3)

            if len(vertices) > 0 and len(faces) > 0:
                all_meshes.append((vertices, faces))

    return all_meshes


def ai2thor_to_pyvista_mesh(vertices, faces):
    """Convert AI2Thor mesh data to PyVista mesh"""
    # Create faces array for PyVista (prepend triangle vertex count)
    pv_faces = []
    for face in faces:
        pv_faces.extend([3, face[0], face[1], face[2]])

    return pv.PolyData(vertices, pv_faces)


def create_floor_from_ai2thor(controller, scene_name='FloorPlan301'):
    """Create a single floor mesh from AI2Thor scene"""
    print(f"Extracting mesh from {scene_name}...")

    # Initialize controller
    event = controller.step(dict(
        action='Initialize',
        gridSize=0.25,
        agentCount=1,
        scene=scene_name
    ))

    # For now, create a simple floor representation based on scene bounds
    # This is a placeholder - you may need to use Unity mesh export for full geometry
    floor_size_x = 10.0
    floor_size_z = 10.0
    floor_height = 3.0  # Height of one floor

    # Create a simple house representation
    floor_mesh = create_simple_house_mesh(floor_size_x, floor_size_z, floor_height)

    return floor_mesh


def create_simple_house_mesh(size_x, size_z, height):
    """Create a simple house mesh representation"""
    # Main house box
    house = pv.Cube(center=(0, height/2, 0), x_length=size_x, y_length=height, z_length=size_z)

    # Create hollow interior by subtracting a smaller box
    interior = pv.Cube(
        center=(0, height/2, 0),
        x_length=size_x - 0.5,
        y_length=height - 0.3,
        z_length=size_z - 0.5
    )

    # Create windows
    windows = []
    window_size = 1.5
    for i in range(3):
        for side in [-1, 1]:
            # Front/back windows
            window = pv.Cube(
                center=(i * 3 - 3, height/2 + 0.5, side * (size_z/2)),
                x_length=window_size,
                y_length=1.5,
                z_length=0.3
            )
            windows.append(window)

            # Side windows
            window = pv.Cube(
                center=(side * (size_x/2), height/2 + 0.5, i * 3 - 3),
                x_length=0.3,
                y_length=1.5,
                z_length=window_size
            )
            windows.append(window)

    # Door on front
    door = pv.Cube(
        center=(0, 1, -(size_z/2)),
        x_length=1.2,
        y_length=2.2,
        z_length=0.3
    )

    return house, windows, door


def create_stairwell(num_floors, floor_height=3.0, stair_x=8.0, stair_z=0.0):
    """Create a stairwell connecting all floors"""
    print(f"Creating stairwell for {num_floors} floors...")

    # Stairwell shaft
    shaft_width = 2.5
    shaft_depth = 4.0
    total_height = num_floors * floor_height

    # Main stairwell enclosure
    stairwell_outer = pv.Cube(
        center=(stair_x, total_height/2, stair_z),
        x_length=shaft_width,
        y_length=total_height,
        z_length=shaft_depth
    )

    # Interior space
    stairwell_inner = pv.Cube(
        center=(stair_x, total_height/2, stair_z),
        x_length=shaft_width - 0.4,
        y_length=total_height,
        z_length=shaft_depth - 0.4
    )

    # Create individual stairs
    stairs = []
    steps_per_floor = 15
    step_height = floor_height / steps_per_floor
    step_depth = shaft_depth / steps_per_floor

    for floor in range(num_floors - 1):
        for step in range(steps_per_floor):
            step_y = floor * floor_height + step * step_height
            step_z = stair_z - shaft_depth/2 + step * step_depth

            stair_step = pv.Cube(
                center=(stair_x, step_y + step_height/2, step_z),
                x_length=shaft_width - 0.5,
                y_length=step_height,
                z_length=step_depth * 1.2
            )
            stairs.append(stair_step)

    return stairwell_outer, stairwell_inner, stairs


def create_4story_building():
    """Main function to create a 4-story building"""
    print("Creating 4-story building with AI2Thor and PyVista...")

    # Initialize AI2Thor controller
    controller = tc.Controller(
        width=800,
        height=600,
        quality='Ultra'
    )

    # Parameters
    num_floors = 4
    floor_height = 3.0
    size_x = 10.0
    size_z = 10.0

    # Create the plotter
    plotter = pv.Plotter()

    # Create and stack floors
    all_floor_meshes = []
    all_windows = []
    all_doors = []

    for floor_num in range(num_floors):
        print(f"Creating floor {floor_num + 1}...")

        # Create floor mesh
        house_mesh, windows, door = create_simple_house_mesh(size_x, size_z, floor_height)

        # Translate to correct height
        translation = [0, floor_num * floor_height, 0]
        house_mesh = house_mesh.translate(translation)

        # Translate windows and door
        translated_windows = [w.translate(translation) for w in windows]
        translated_door = door.translate(translation)

        all_floor_meshes.append(house_mesh)
        all_windows.extend(translated_windows)
        all_doors.append(translated_door)

        # Add to plotter
        plotter.add_mesh(house_mesh, color='tan', opacity=0.7, label=f'Floor {floor_num + 1}')

    # Add windows
    for i, window in enumerate(all_windows):
        plotter.add_mesh(window, color='lightblue', opacity=0.6)

    # Add doors
    for i, door in enumerate(all_doors):
        plotter.add_mesh(door, color='brown', opacity=0.8)

    # Create stairwell
    stairwell_outer, stairwell_inner, stairs = create_stairwell(num_floors, floor_height)
    plotter.add_mesh(stairwell_outer, color='gray', opacity=0.5, label='Stairwell')

    # Add individual stairs
    for i, stair in enumerate(stairs):
        plotter.add_mesh(stair, color='darkgray', opacity=0.9)

    # Combine all meshes into one unified building
    print("Combining all meshes into unified building...")
    combined_building = all_floor_meshes[0]

    for floor_mesh in all_floor_meshes[1:]:
        combined_building = combined_building + floor_mesh

    for window in all_windows:
        combined_building = combined_building + window

    for door in all_doors:
        combined_building = combined_building + door

    combined_building = combined_building + stairwell_outer

    for stair in stairs:
        combined_building = combined_building + stair

    # Save combined building
    output_file = 'unified_4story_building.vtk'
    combined_building.save(output_file)
    print(f"Saved unified building to {output_file}")

    # Also save as STL for better compatibility
    combined_building.save('unified_4story_building.stl')
    print("Saved unified building to unified_4story_building.stl")

    # Configure plotter
    plotter.add_text("4-Story Building with Connected Stairwell", position='upper_left', font_size=12)
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

    # Show the result
    print("Displaying building...")
    plotter.show()

    # Cleanup
    controller.stop()

    return combined_building


if __name__ == "__main__":
    building = create_4story_building()
    print("\n4-story building creation complete!")
    print(f"Total vertices: {building.n_points}")
    print(f"Total cells: {building.n_cells}")
