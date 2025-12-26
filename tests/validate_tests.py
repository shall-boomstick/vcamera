#!/usr/bin/env python3
"""Test validation script for Virtual Camera Server test suite.

This script validates that:
1. All test files are present
2. Dependencies are available
3. Tests can be collected
4. Test structure is correct
"""

import os
import sys
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.RESET} {text}")


def check_test_files():
    """Check that all expected test files exist."""
    print_header("Checking Test Files")
    
    test_dir = Path(__file__).parent
    expected_files = {
        'unit': [
            'test_models.py',
            'test_storage.py',
            'test_auth_service.py',
            'test_video_library_service.py',
            'test_camera_manager_service.py',
        ],
        'integration': [
            'test_video_library_integration.py',
            'test_camera_lifecycle.py',
            'test_auth_integration.py',
        ],
        'user': [
            'test_web_interface.py',
        ],
    }
    
    all_present = True
    
    for category, files in expected_files.items():
        category_dir = test_dir / category
        if not category_dir.exists():
            print_error(f"Test directory missing: {category}/")
            all_present = False
            continue
        
        for file in files:
            file_path = category_dir / file
            if file_path.exists():
                print_success(f"{category}/{file}")
            else:
                print_error(f"{category}/{file} - MISSING")
                all_present = False
    
    # Check conftest.py
    conftest = test_dir / 'conftest.py'
    if conftest.exists():
        print_success("conftest.py")
    else:
        print_error("conftest.py - MISSING")
        all_present = False
    
    return all_present


def check_dependencies():
    """Check that required dependencies are available."""
    print_header("Checking Dependencies")
    
    dependencies = {
        'pytest': 'pytest',
        'opencv': 'cv2',
        'flask': 'flask',
    }
    
    all_available = True
    
    for name, module in dependencies.items():
        try:
            __import__(module)
            print_success(f"{name} ({module})")
        except ImportError:
            print_error(f"{name} ({module}) - NOT INSTALLED")
            all_available = False
    
    return all_available


def check_test_collection():
    """Check that pytest can collect tests."""
    print_header("Checking Test Collection")
    
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    try:
        result = subprocess.run(
            ['python3', '-m', 'pytest', '--collect-only', '-q'],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Count collected tests
            output_lines = result.stdout.split('\n')
            test_count = 0
            for line in output_lines:
                if 'test_' in line and ('<Function' in line or '<Class' in line):
                    test_count += 1
            
            print_success(f"Test collection successful ({test_count} tests found)")
            return True
        else:
            print_error("Test collection failed")
            print(f"Error output:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Test collection timed out")
        return False
    except FileNotFoundError:
        print_error("pytest not found in PATH")
        return False
    except Exception as e:
        print_error(f"Error during test collection: {e}")
        return False


def check_test_structure():
    """Check test directory structure."""
    print_header("Checking Test Structure")
    
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    # Check pytest.ini
    pytest_ini = project_root / 'pytest.ini'
    if pytest_ini.exists():
        print_success("pytest.ini exists")
    else:
        print_warning("pytest.ini not found (optional)")
    
    # Check requirements.txt includes pytest
    requirements = project_root / 'requirements.txt'
    if requirements.exists():
        with open(requirements, 'r') as f:
            content = f.read()
            if 'pytest' in content:
                print_success("pytest in requirements.txt")
            else:
                print_warning("pytest not found in requirements.txt")
    
    return True


def main():
    """Run all validation checks."""
    print(f"\n{Colors.BOLD}Virtual Camera Server - Test Validation{Colors.RESET}")
    print(f"Test Directory: {Path(__file__).parent}")
    
    results = {
        'test_files': check_test_files(),
        'dependencies': check_dependencies(),
        'test_structure': check_test_structure(),
    }
    
    # Only try test collection if dependencies are available
    if results['dependencies']:
        results['test_collection'] = check_test_collection()
    else:
        print_header("Skipping Test Collection")
        print_warning("Test collection skipped due to missing dependencies")
        results['test_collection'] = False
    
    # Summary
    print_header("Validation Summary")
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = print_success if passed else print_error
        status(f"{check.replace('_', ' ').title()}")
    
    if all_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All checks passed!{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some checks failed. See details above.{Colors.RESET}\n")
        print("To fix dependency issues, run:")
        print("  source venv/bin/activate")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())

