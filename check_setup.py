#!/usr/bin/env python3
"""
RescuNav Setup Checker
Checks what's installed and what's missing
"""

import sys
import os

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, None

def check_env_var(var_name):
    """Check if environment variable is set"""
    from dotenv import load_dotenv
    load_dotenv()
    value = os.getenv(var_name)
    return bool(value and value.strip()), value

def main():
    print("=" * 70)
    print("RESCUNAV SETUP STATUS CHECK")
    print("=" * 70)
    print()
    
    # Check Python version
    print("Python Version:")
    print(f"  {sys.version}")
    if sys.version_info < (3, 8):
        print("  ⚠️  WARNING: Python 3.8+ recommended")
    else:
        print("  ✓ Version OK")
    print()
    
    # Core dependencies
    print("=" * 70)
    print("CORE DEPENDENCIES (Required)")
    print("=" * 70)
    
    core_packages = [
        ('networkx', 'networkx', 'Graph algorithms for pathfinding'),
        ('numpy', 'numpy', 'Numerical computing'),
        ('scipy', 'scipy', 'Scientific computing'),
        ('matplotlib', 'matplotlib', 'Plotting and visualization'),
        ('requests', 'requests', 'HTTP requests'),
    ]
    
    core_installed = 0
    for pkg_name, import_name, description in core_packages:
        installed, version = check_package(pkg_name, import_name)
        if installed:
            print(f"✓ {pkg_name:20s} {version:15s} - {description}")
            core_installed += 1
        else:
            print(f"✗ {pkg_name:20s} {'NOT INSTALLED':15s} - {description}")
    
    print()
    print(f"Core Status: {core_installed}/{len(core_packages)} installed")
    print()
    
    # Web & Database
    print("=" * 70)
    print("WEB & DATABASE (For full features)")
    print("=" * 70)
    
    web_packages = [
        ('flask', 'flask', 'Web server for UI'),
        ('pymongo', 'pymongo', 'MongoDB database'),
        ('python-dotenv', 'dotenv', 'Environment variables'),
        ('opencv-python', 'cv2', 'Video processing'),
    ]
    
    web_installed = 0
    for pkg_name, import_name, description in web_packages:
        installed, version = check_package(pkg_name, import_name)
        if installed:
            print(f"✓ {pkg_name:20s} {version:15s} - {description}")
            web_installed += 1
        else:
            print(f"✗ {pkg_name:20s} {'NOT INSTALLED':15s} - {description}")
    
    print()
    print(f"Web/DB Status: {web_installed}/{len(web_packages)} installed")
    print()
    
    # Optional advanced
    print("=" * 70)
    print("OPTIONAL ADVANCED (Not required)")
    print("=" * 70)
    
    optional_packages = [
        ('pyvista', 'pyvista', '3D visualization'),
        ('trimesh', 'trimesh', '3D mesh processing'),
        ('ai2thor', 'ai2thor', '3D simulation'),
        ('torch', 'torch', 'Deep learning'),
        ('transformers', 'transformers', 'NLP models'),
    ]
    
    optional_installed = 0
    for pkg_name, import_name, description in optional_packages:
        installed, version = check_package(pkg_name, import_name)
        if installed:
            print(f"✓ {pkg_name:20s} {version:15s} - {description}")
            optional_installed += 1
        else:
            print(f"⚪ {pkg_name:20s} {'NOT INSTALLED':15s} - {description}")
    
    print()
    print(f"Optional Status: {optional_installed}/{len(optional_packages)} installed")
    print()
    
    # API Keys
    print("=" * 70)
    print("API KEYS & CONFIGURATION")
    print("=" * 70)
    
    # Check if dotenv is available
    dotenv_available, _ = check_package('python-dotenv', 'dotenv')
    
    if dotenv_available:
        configs = [
            ('FIREWORKS_API_KEY', 'Fireworks AI (video analysis)'),
            ('MONGODB_URI', 'MongoDB Atlas (database)'),
        ]
        
        configs_set = 0
        for var_name, description in configs:
            is_set, value = check_env_var(var_name)
            if is_set:
                # Show first 10 chars only
                display_value = value[:10] + '...' if len(value) > 10 else value
                print(f"✓ {var_name:20s} SET - {description}")
                configs_set += 1
            else:
                print(f"✗ {var_name:20s} NOT SET - {description}")
        
        print()
        print(f"Config Status: {configs_set}/{len(configs)} configured")
    else:
        print("⚠️  python-dotenv not installed - cannot check .env file")
    
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_core = len(core_packages)
    total_web = len(web_packages)
    
    if core_installed == total_core and web_installed == total_web:
        print("✅ FULL SETUP COMPLETE")
        print("   All required dependencies installed!")
        print()
        print("   You can run:")
        print("   - python test_rescue_system.py")
        print("   - python rescue_simulation.py --scenario fire --iterations 3")
        print("   - python web_app.py")
    elif core_installed == total_core:
        print("⚠️  PARTIAL SETUP")
        print("   Core dependencies installed, but missing web/database packages")
        print()
        print("   You can run:")
        print("   - python building_navigator.py")
        print("   - python danger_simulator.py")
        print()
        print("   To enable full features, install:")
        print("   pip install flask pymongo python-dotenv opencv-python")
    elif core_installed > 0:
        print("⚠️  INCOMPLETE SETUP")
        print("   Some core dependencies missing")
        print()
        print("   To complete setup, install:")
        missing_core = [pkg for pkg, imp, desc in core_packages 
                       if not check_package(pkg, imp)[0]]
        for pkg in missing_core:
            print(f"   pip install {pkg}")
    else:
        print("❌ NO SETUP")
        print("   No dependencies installed")
        print()
        print("   Quick setup:")
        print("   pip install networkx pymongo flask opencv-python python-dotenv")
    
    print()
    print("=" * 70)
    print("For detailed setup instructions, see: SETUP_STATUS_REPORT.md")
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()
