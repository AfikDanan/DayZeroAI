"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def project_root():
    """Project root directory fixture"""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_output_dir():
    """Test output directory fixture"""
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)
    return output_dir

@pytest.fixture
def sample_employee_data():
    """Sample employee data for testing"""
    from datetime import date
    return {
        "employee_id": "TEST001",
        "name": "Test Employee",
        "email": "test@company.com",
        "position": "Software Engineer",
        "team": "Engineering",
        "manager": "Test Manager",
        "start_date": date(2025, 10, 20),
        "office": "Test Office",
        "tech_stack": ["Python", "FastAPI"],
        "first_day_schedule": [
            {
                "time": "9:00 AM",
                "activity": "Welcome & Orientation"
            }
        ],
        "first_week_schedule": {
            "Monday": "Onboarding and Setup"
        }
    }

@pytest.fixture
def mock_webhook_payload(sample_employee_data):
    """Mock webhook payload for testing"""
    from datetime import datetime
    return {
        "event_type": "user.onboarding",
        "employee_data": sample_employee_data,
        "timestamp": datetime.now().isoformat()
    }

# Test markers
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (require services)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (require all external services)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (may take several minutes)"
    )