#!/usr/bin/env python3
"""
Master test runner for 4-story building connectivity tests.
Provides menu to run all test scripts in sequence or individually.
"""

import os
import sys
import subprocess


def print_header():
    print("=" * 70)
    print(" " * 15 + "4-STORY BUILDING TEST SUITE")
    print(" " * 18 + "Connectivity & Structure")
    print("=" * 70)
    print()


def check_building_exists():
    """Check if a building file exists"""
    building_files = [
        'ai2thor_4story_building.vtk',
        'unified_4story_building.vtk'
    ]

    for fname in building_files:
        if os.path.exists(fname):
            size_mb = os.path.getsize(fname) / (1024 * 1024)
            return fname, size_mb

    return None, 0


def print_status():
    """Print current status"""
    building_file, size_mb = check_building_exists()

    print("STATUS:")
    print("-" * 70)

    if building_file:
        print(f"✓ Building file found: {building_file} ({size_mb:.2f} MB)")
        print("  Ready to run tests!")
    else:
        print("✗ No building file found!")
        print("  Please generate a building first:")
        print("    python create_4story_advanced.py")
        print("    OR")
        print("    python run_building_generator.py")

    print("-" * 70)
    print()


def print_menu():
    """Print test menu"""
    print("AVAILABLE TESTS:")
    print("-" * 70)
    print()
    print("  [1] Simple Path Visualization (QUICK)")
    print("      → Static display of navigation path")
    print("      → Shows complete route through all floors")
    print("      → Best for quick verification")
    print()
    print("  [2] Animated Floor Navigation (DEMO)")
    print("      → Agent moves through building in real-time")
    print("      → Demonstrates stair climbing")
    print("      → Interactive and engaging")
    print()
    print("  [3] Wall & Floor Separation Analysis (DETAILED)")
    print("      → Cross-sections and structural analysis")
    print("      → Shows floor and wall divisions")
    print("      → Proves structural integrity")
    print()
    print("  [4] Run All Tests in Sequence (COMPREHENSIVE)")
    print("      → Executes all three tests")
    print("      → Complete verification")
    print()
    print("  [5] Generate Building First")
    print("      → Run building generator")
    print()
    print("  [6] View Building (No Tests)")
    print("      → Just view the 3D model")
    print()
    print("  [0] Exit")
    print()
    print("-" * 70)
    print()


def run_test_script(script_name, description):
    """Run a test script"""
    print("\n" + "=" * 70)
    print(f"RUNNING: {description}")
    print("=" * 70)
    print()

    if not os.path.exists(script_name):
        print(f"Error: Script '{script_name}' not found!")
        return False

    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            check=False
        )

        success = result.returncode == 0

        if success:
            print("\n✓ Test completed successfully!")
        else:
            print(f"\n✗ Test exited with code {result.returncode}")

        return success

    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n✗ Error running test: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "=" * 70)
    print("RUNNING COMPLETE TEST SUITE")
    print("=" * 70)
    print()

    tests = [
        ('test_simple_path.py', 'Simple Path Visualization'),
        ('test_floor_connectivity.py', 'Animated Navigation'),
        ('test_wall_floor_separation.py', 'Structural Analysis')
    ]

    results = {}

    for i, (script, description) in enumerate(tests, 1):
        print(f"\n[{i}/{len(tests)}] {description}")
        print("-" * 70)

        success = run_test_script(script, description)
        results[description] = success

        if i < len(tests):
            try:
                input("\nPress Enter to continue to next test (Ctrl+C to skip)...")
            except KeyboardInterrupt:
                print("\n\nSkipping remaining tests...")
                break

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)

    for test_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status:10} - {test_name}")

    passed = sum(1 for s in results.values() if s)
    total = len(results)

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ ALL TESTS PASSED - Building is fully functional!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed - Review errors above")

    print("=" * 70)


def main():
    """Main menu loop"""
    print_header()

    while True:
        print_status()
        print_menu()

        try:
            choice = input("Select option [0-6]: ").strip()
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break

        print()

        if choice == '0':
            print("Exiting. Goodbye!")
            break

        elif choice == '1':
            # Simple path visualization
            building_file, _ = check_building_exists()
            if not building_file:
                print("⚠ Please generate a building first (option 5)")
                input("\nPress Enter to continue...")
                continue

            run_test_script('test_simple_path.py', 'Simple Path Visualization')
            input("\nPress Enter to continue...")

        elif choice == '2':
            # Animated navigation
            building_file, _ = check_building_exists()
            if not building_file:
                print("⚠ Please generate a building first (option 5)")
                input("\nPress Enter to continue...")
                continue

            run_test_script('test_floor_connectivity.py', 'Animated Navigation')
            input("\nPress Enter to continue...")

        elif choice == '3':
            # Wall & floor separation
            building_file, _ = check_building_exists()
            if not building_file:
                print("⚠ Please generate a building first (option 5)")
                input("\nPress Enter to continue...")
                continue

            run_test_script('test_wall_floor_separation.py', 'Structural Analysis')
            input("\nPress Enter to continue...")

        elif choice == '4':
            # Run all tests
            building_file, _ = check_building_exists()
            if not building_file:
                print("⚠ Please generate a building first (option 5)")
                input("\nPress Enter to continue...")
                continue

            run_all_tests()
            input("\nPress Enter to continue...")

        elif choice == '5':
            # Generate building
            print("Launching building generator...")
            run_test_script('run_building_generator.py', 'Building Generator')
            input("\nPress Enter to continue...")

        elif choice == '6':
            # View building
            building_file, _ = check_building_exists()
            if not building_file:
                print("⚠ Please generate a building first (option 5)")
                input("\nPress Enter to continue...")
                continue

            run_test_script('view_building.py', 'Building Viewer')
            input("\nPress Enter to continue...")

        else:
            print("Invalid choice. Please select 0-6.")
            input("\nPress Enter to continue...")

        print("\n")


if __name__ == "__main__":
    main()
