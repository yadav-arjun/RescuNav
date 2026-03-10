#!/usr/bin/env python3
"""
Interactive launcher for 4-story building generators
"""

import sys
import os

def print_header():
    print("=" * 70)
    print(" " * 15 + "4-STORY BUILDING GENERATOR")
    print(" " * 10 + "AI2Thor + PyVista Integration")
    print("=" * 70)
    print()

def print_menu():
    print("Select which version to run:")
    print()
    print("  [1] Basic Version")
    print("      - Quick generation")
    print("      - Simplified geometry")
    print("      - Good for testing")
    print()
    print("  [2] Advanced Version (Recommended)")
    print("      - AI2Thor scene analysis")
    print("      - Realistic geometry")
    print("      - Multiple output formats")
    print()
    print("  [3] Both versions (compare)")
    print()
    print("  [0] Exit")
    print()

def run_basic():
    print("\n" + "=" * 70)
    print("Running BASIC version...")
    print("=" * 70 + "\n")

    try:
        import create_4story_building
        building = create_4story_building.create_4story_building()
        print("\n✓ Basic version completed successfully!")
        return True
    except Exception as e:
        print(f"\n✗ Error running basic version: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_advanced():
    print("\n" + "=" * 70)
    print("Running ADVANCED version...")
    print("=" * 70 + "\n")

    try:
        import create_4story_advanced
        building = create_4story_advanced.create_4story_building_from_ai2thor()
        print("\n✓ Advanced version completed successfully!")
        return True
    except Exception as e:
        print(f"\n✗ Error running advanced version: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_dependencies():
    """Check if required packages are installed"""
    missing = []

    try:
        import ai2thor
    except ImportError:
        missing.append('ai2thor')

    try:
        import pyvista
    except ImportError:
        missing.append('pyvista')

    try:
        import numpy
    except ImportError:
        missing.append('numpy')

    if missing:
        print("⚠ Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print()
        print("Install with:")
        print(f"  pip install {' '.join(missing)}")
        print()
        return False

    return True

def main():
    print_header()

    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies and try again.")
        return

    print("✓ All dependencies found")
    print()

    while True:
        print_menu()

        try:
            choice = input("Enter your choice [0-3]: ").strip()
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)

        print()

        if choice == '0':
            print("Exiting. Goodbye!")
            break

        elif choice == '1':
            success = run_basic()
            if success:
                print("\nGenerated files:")
                if os.path.exists('unified_4story_building.vtk'):
                    print("  ✓ unified_4story_building.vtk")
                if os.path.exists('unified_4story_building.stl'):
                    print("  ✓ unified_4story_building.stl")
            input("\nPress Enter to continue...")
            print("\n")

        elif choice == '2':
            success = run_advanced()
            if success:
                print("\nGenerated files:")
                if os.path.exists('ai2thor_4story_building.vtk'):
                    print("  ✓ ai2thor_4story_building.vtk")
                if os.path.exists('ai2thor_4story_building.stl'):
                    print("  ✓ ai2thor_4story_building.stl")
                if os.path.exists('ai2thor_4story_building.ply'):
                    print("  ✓ ai2thor_4story_building.ply")
            input("\nPress Enter to continue...")
            print("\n")

        elif choice == '3':
            print("Running both versions...\n")

            print("Step 1/2: Basic version")
            basic_success = run_basic()

            print("\n" + "-" * 70 + "\n")

            print("Step 2/2: Advanced version")
            advanced_success = run_advanced()

            print("\n" + "=" * 70)
            print("COMPARISON SUMMARY")
            print("=" * 70)
            print(f"Basic version:    {'✓ Success' if basic_success else '✗ Failed'}")
            print(f"Advanced version: {'✓ Success' if advanced_success else '✗ Failed'}")

            if basic_success or advanced_success:
                print("\nGenerated files:")
                for fname in [
                    'unified_4story_building.vtk',
                    'unified_4story_building.stl',
                    'ai2thor_4story_building.vtk',
                    'ai2thor_4story_building.stl',
                    'ai2thor_4story_building.ply'
                ]:
                    if os.path.exists(fname):
                        size_mb = os.path.getsize(fname) / (1024 * 1024)
                        print(f"  ✓ {fname} ({size_mb:.2f} MB)")

            input("\nPress Enter to continue...")
            print("\n")

        else:
            print("Invalid choice. Please enter 0, 1, 2, or 3.")
            print()

if __name__ == "__main__":
    main()
