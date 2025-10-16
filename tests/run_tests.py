#!/usr/bin/env python3
"""
Test Runner Script

Provides different test execution modes for the preboarding service.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_unit_tests():
    """Run unit tests only (fast, no external dependencies)"""
    print("🧪 Running Unit Tests")
    print("=" * 40)
    cmd = ["python", "-m", "pytest", "unit/", "-v", "-m", "unit"]
    return subprocess.run(cmd, cwd=Path(__file__).parent)

def run_integration_tests():
    """Run integration tests (require Redis and API server)"""
    print("🔗 Running Integration Tests")
    print("=" * 40)
    print("⚠️  Make sure Redis and API server are running!")
    cmd = ["python", "-m", "pytest", "integration/", "-v", "-m", "integration"]
    return subprocess.run(cmd, cwd=Path(__file__).parent)

def run_e2e_tests():
    """Run end-to-end tests (require all external services)"""
    print("🎬 Running End-to-End Tests")
    print("=" * 40)
    print("⚠️  Make sure all services are running (Redis, API, OpenAI, Google Cloud)!")
    cmd = ["python", "-m", "pytest", "e2e/", "-v", "-m", "e2e"]
    return subprocess.run(cmd, cwd=Path(__file__).parent)

def run_all_tests():
    """Run all tests"""
    print("🚀 Running All Tests")
    print("=" * 40)
    cmd = ["python", "-m", "pytest", "-v"]
    return subprocess.run(cmd, cwd=Path(__file__).parent)

def run_quick_tests():
    """Run quick tests only (unit + basic integration)"""
    print("⚡ Running Quick Tests")
    print("=" * 40)
    cmd = ["python", "-m", "pytest", "unit/", "integration/test_basic_api.py", "-v"]
    return subprocess.run(cmd, cwd=Path(__file__).parent)

def validate_setup():
    """Run setup validation"""
    print("✅ Validating Setup")
    print("=" * 40)
    cmd = ["python", "utils/check_setup.py"]
    return subprocess.run(cmd, cwd=Path(__file__).parent)

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Preboarding Service Test Runner")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "e2e", "all", "quick", "setup"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    print("🧪 Preboarding Service Test Runner")
    print("=" * 50)
    
    if args.test_type == "unit":
        result = run_unit_tests()
    elif args.test_type == "integration":
        result = run_integration_tests()
    elif args.test_type == "e2e":
        result = run_e2e_tests()
    elif args.test_type == "all":
        result = run_all_tests()
    elif args.test_type == "quick":
        result = run_quick_tests()
    elif args.test_type == "setup":
        result = validate_setup()
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())