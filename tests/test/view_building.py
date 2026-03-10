#!/usr/bin/env python3
"""
Simple viewer for generated 4-story building files
"""

import pyvista as pv
import os
import sys

def view_building(filename):
    """Load and visualize a building file"""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found!")
        return False

    print(f"Loading {filename}...")

    # Load the mesh
    try:
        mesh = pv.read(filename)
    except Exception as e:
        print(f"Error loading file: {e}")
        return False

    # Print statistics
    print("\nBuilding Statistics:")
    print(f"  Vertices: {mesh.n_points:,}")
    print(f"  Faces: {mesh.n_cells:,}")

    bounds = mesh.bounds
    width = bounds[1] - bounds[0]
    depth = bounds[3] - bounds[2]
    height = bounds[5] - bounds[4]

    print(f"  Dimensions:")
    print(f"    Width (X):  {width:.2f}m")
    print(f"    Depth (Z):  {depth:.2f}m")
    print(f"    Height (Y): {height:.2f}m")
    print(f"  Volume: {mesh.volume:.2f} m³")

    # Create plotter
    plotter = pv.Plotter()
    plotter.add_text(
        f"Building Viewer - {os.path.basename(filename)}",
        position='upper_left',
        font_size=12,
        color='white'
    )

    # Add the mesh with nice styling
    plotter.add_mesh(
        mesh,
        color='tan',
        opacity=0.9,
        show_edges=True,
        edge_color='darkgray',
        line_width=0.5
    )

    # Add coordinate axes
    plotter.add_axes()
    plotter.show_grid()

    # Setup camera for proper building orientation (floor 0 at bottom, top floor at top)
    center_x = (bounds[0] + bounds[1]) / 2
    center_y = (bounds[2] + bounds[3]) / 2
    center_z = (bounds[4] + bounds[5]) / 2

    # Position camera to look at building from an angle, with Y-axis pointing up
    plotter.camera_position = [
        (center_x + 20, center_y + 15, center_z + 20),  # Camera position
        (center_x, center_y, center_z),  # Focal point
        (0, 1, 0)  # Up vector (Y-axis points up)
    ]

    # Add useful keyboard shortcuts info
    print("\nViewer Controls:")
    print("  Left-click + drag : Rotate")
    print("  Right-click + drag: Pan")
    print("  Scroll wheel      : Zoom")
    print("  'r'               : Reset camera")
    print("  's'               : Take screenshot")
    print("  'q' or ESC        : Quit")

    # Show
    print("\nDisplaying building...")
    plotter.show()

    return True

def list_available_buildings():
    """List all available building files in the current directory"""
    extensions = ['.vtk', '.stl', '.ply', '.obj']
    files = []

    for ext in extensions:
        for fname in os.listdir('.'):
            if fname.endswith(ext) and 'building' in fname.lower():
                size_mb = os.path.getsize(fname) / (1024 * 1024)
                files.append((fname, size_mb))

    return files

def main():
    print("=" * 70)
    print(" " * 20 + "BUILDING VIEWER")
    print("=" * 70)
    print()

    # Check for command line argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        view_building(filename)
        return

    # List available files
    available = list_available_buildings()

    if not available:
        print("No building files found in the current directory.")
        print()
        print("Looking for files with extensions: .vtk, .stl, .ply, .obj")
        print("And containing 'building' in the filename.")
        print()
        print("Run one of the building generators first:")
        print("  python create_4story_building.py")
        print("  python create_4story_advanced.py")
        print("  python run_building_generator.py")
        return

    print("Available building files:")
    print()

    for i, (fname, size_mb) in enumerate(available, 1):
        print(f"  [{i}] {fname} ({size_mb:.2f} MB)")

    print()
    print(f"  [0] Exit")
    print()

    try:
        choice = input("Select a file to view [0-{}]: ".format(len(available))).strip()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        return

    print()

    if choice == '0':
        print("Exiting.")
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(available):
            filename = available[idx][0]
            view_building(filename)
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
