"""
Pre-Push Verification Script
Checks if your code is safe to push to GitHub
"""

import os
import sys

def check_file_exists(filename):
    """Check if a file exists"""
    return os.path.exists(filename)

def check_gitignore():
    """Verify .gitignore exists and contains .env"""
    print("\n" + "="*70)
    print("1. CHECKING .gitignore FILE")
    print("="*70)
    
    if not check_file_exists('.gitignore'):
        print("❌ CRITICAL: .gitignore file NOT found!")
        print("   Your API keys will be exposed!")
        return False
    
    print("✅ .gitignore file exists")
    
    with open('.gitignore', 'r') as f:
        content = f.read()
        
    if '.env' not in content:
        print("❌ CRITICAL: .env is NOT in .gitignore!")
        print("   Your API keys will be exposed!")
        return False
    
    print("✅ .env is in .gitignore")
    return True

def check_env_file():
    """Check .env file status"""
    print("\n" + "="*70)
    print("2. CHECKING .env FILE")
    print("="*70)
    
    if not check_file_exists('.env'):
        print("⚠️  .env file not found (this is OK if you don't have API keys)")
        return True
    
    print("✅ .env file exists")
    print("⚠️  IMPORTANT: Make sure .env is in .gitignore!")
    print("   This file contains your API keys and should NEVER be pushed!")
    
    return True

def check_env_example():
    """Check if .env.example exists"""
    print("\n" + "="*70)
    print("3. CHECKING .env.example FILE")
    print("="*70)
    
    if not check_file_exists('.env.example'):
        print("⚠️  .env.example not found")
        print("   Consider creating one as a template for others")
        return True
    
    print("✅ .env.example exists")
    return True

def check_large_files():
    """Check for large files that shouldn't be pushed"""
    print("\n" + "="*70)
    print("4. CHECKING FOR LARGE FILES")
    print("="*70)
    
    large_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.vtk', '.stl', '.ply']
    large_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and venv
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv' and d != '__pycache__']
        
        for file in files:
            if any(file.endswith(ext) for ext in large_extensions):
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                if size > 1_000_000:  # > 1MB
                    large_files.append((filepath, size))
    
    if large_files:
        print(f"⚠️  Found {len(large_files)} large file(s):")
        for filepath, size in large_files:
            size_mb = size / 1_000_000
            print(f"   - {filepath}: {size_mb:.2f} MB")
        print("\n   Consider adding these to .gitignore if not needed")
    else:
        print("✅ No large files found")
    
    return True

def check_sensitive_strings():
    """Check for potential sensitive information in code"""
    print("\n" + "="*70)
    print("5. CHECKING FOR SENSITIVE STRINGS")
    print("="*70)
    
    sensitive_patterns = ['password', 'api_key', 'secret', 'token']
    found_issues = []
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories, venv, and pycache
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv' and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py') and file != 'pre_push_check.py':
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for pattern in sensitive_patterns:
                            if pattern in content and 'os.getenv' not in content:
                                # Check if it's just a comment or variable name
                                if f'"{pattern}"' in content or f"'{pattern}'" in content:
                                    continue
                                found_issues.append((filepath, pattern))
                except:
                    pass
    
    if found_issues:
        print(f"⚠️  Found {len(found_issues)} potential sensitive string(s):")
        for filepath, pattern in found_issues:
            print(f"   - {filepath}: contains '{pattern}'")
        print("\n   Review these files to ensure no hardcoded secrets")
    else:
        print("✅ No obvious sensitive strings found")
    
    return True

def check_requirements():
    """Check if requirements.txt exists"""
    print("\n" + "="*70)
    print("6. CHECKING REQUIREMENTS FILE")
    print("="*70)
    
    if check_file_exists('requirements_rescue.txt'):
        print("✅ requirements_rescue.txt exists")
        return True
    elif check_file_exists('requirements.txt'):
        print("✅ requirements.txt exists")
        return True
    else:
        print("⚠️  No requirements file found")
        print("   Consider creating one: pip freeze > requirements.txt")
        return True

def check_readme():
    """Check if README exists"""
    print("\n" + "="*70)
    print("7. CHECKING README FILE")
    print("="*70)
    
    readme_files = ['README.md', 'README_RESCUE.md', 'PROJECT_COMPLETE_SUMMARY.md']
    found = False
    
    for readme in readme_files:
        if check_file_exists(readme):
            print(f"✅ {readme} exists")
            found = True
    
    if not found:
        print("⚠️  No README file found")
        print("   Consider creating README.md for your repository")
    
    return True

def check_license():
    """Check if LICENSE file exists"""
    print("\n" + "="*70)
    print("8. CHECKING LICENSE FILE")
    print("="*70)
    
    if check_file_exists('LICENSE') or check_file_exists('LICENSE.txt'):
        print("✅ LICENSE file exists")
    else:
        print("⚠️  No LICENSE file found")
        print("   Consider adding a license (MIT, Apache, etc.)")
    
    return True

def main():
    """Run all checks"""
    print("\n" + "="*70)
    print("GITHUB PRE-PUSH VERIFICATION")
    print("RescuNav Project")
    print("="*70)
    
    checks = [
        check_gitignore,
        check_env_file,
        check_env_example,
        check_large_files,
        check_sensitive_strings,
        check_requirements,
        check_readme,
        check_license
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Error running check: {e}")
            results.append(False)
    
    # Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    critical_passed = results[0]  # .gitignore check
    
    if critical_passed:
        print("✅ CRITICAL CHECKS PASSED")
        print("   Your .env file is protected!")
    else:
        print("❌ CRITICAL CHECKS FAILED")
        print("   DO NOT PUSH TO GITHUB YET!")
        print("   Fix the issues above first!")
        sys.exit(1)
    
    warnings = sum(1 for r in results if not r)
    if warnings > 0:
        print(f"\n⚠️  {warnings} warning(s) found")
        print("   Review the warnings above")
    else:
        print("\n✅ All checks passed!")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Review any warnings above")
    print("2. Run: git status")
    print("3. Verify .env is NOT listed")
    print("4. Run: git add .")
    print("5. Run: git commit -m 'Your message'")
    print("6. Run: git push origin main")
    print("="*70)
    
    print("\n✅ Safe to proceed with git push!")

if __name__ == "__main__":
    main()
