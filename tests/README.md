# Test Suite Documentation

## Overview

The preboarding service test suite is organized into different categories to support various testing scenarios and development workflows.

## Test Structure

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_welcome_slide.py      # Welcome slide generation tests
│   ├── test_script_only.py        # Script generation tests
│   └── test_audio_from_script.py  # Audio generation tests
├── integration/             # Integration tests (require services)
│   ├── test_basic_api.py          # Basic API endpoint tests
│   ├── test_webhook.py            # Webhook processing tests
│   └── test_integration.py        # Service integration tests
├── e2e/                     # End-to-end tests (full workflow)
│   ├── test_full_pipeline.py      # Complete pipeline tests
│   ├── test_video_generation.py   # Video generation tests
│   └── test_with_dev_output.py    # Development output tests
├── utils/                   # Utility and debugging scripts
│   ├── check_setup.py             # Setup validation
│   ├── check_queue.py             # Redis queue inspection
│   ├── debug_config.py            # Configuration debugging
│   ├── debug_webhook.py           # Webhook debugging
│   └── start_services.py          # Service startup helper
├── fixtures/                # Test fixtures and mocks
│   ├── test_video_mock.py         # Mock video generation
│   ├── test_dev_output.py         # Development output helpers
│   └── test_video_no_audio.py     # Audio-less testing
└── slides/                  # Test slide outputs
```

## Test Categories

### 🧪 Unit Tests (`unit/`)
- **Purpose**: Test individual components in isolation
- **Speed**: Fast (< 1 second per test)
- **Dependencies**: None (no external services required)
- **Examples**: 
  - Slide generation logic
  - Script parsing functions
  - Data model validation

### 🔗 Integration Tests (`integration/`)
- **Purpose**: Test API endpoints and service interactions
- **Speed**: Medium (1-10 seconds per test)
- **Dependencies**: Redis, API server
- **Examples**:
  - Webhook endpoint responses
  - Job status tracking
  - API error handling

### 🎬 End-to-End Tests (`e2e/`)
- **Purpose**: Test complete workflows from start to finish
- **Speed**: Slow (30+ seconds per test)
- **Dependencies**: All external services (OpenAI, Google Cloud, SendGrid)
- **Examples**:
  - Complete video generation pipeline
  - Webhook to video delivery workflow
  - Error recovery scenarios

### 🛠️ Utilities (`utils/`)
- **Purpose**: Development and debugging tools
- **Usage**: Manual execution for troubleshooting
- **Examples**:
  - Setup validation scripts
  - Configuration debugging
  - Service health checks

### 📦 Fixtures (`fixtures/`)
- **Purpose**: Mock implementations and test data
- **Usage**: Support testing without external dependencies
- **Examples**:
  - Mock API responses
  - Test data generators
  - Development helpers

## Running Tests

### Quick Start
```bash
# Run all unit tests (fastest)
python tests/run_tests.py unit

# Run integration tests (requires Redis + API)
python tests/run_tests.py integration

# Run end-to-end tests (requires all services)
python tests/run_tests.py e2e

# Run quick validation
python tests/run_tests.py quick

# Validate setup
python tests/run_tests.py setup
```

### Using Pytest Directly
```bash
# Run specific test categories
pytest tests/unit/ -m unit
pytest tests/integration/ -m integration
pytest tests/e2e/ -m e2e

# Run specific test files
pytest tests/unit/test_welcome_slide.py
pytest tests/integration/test_basic_api.py

# Run with verbose output
pytest -v tests/unit/

# Run tests matching pattern
pytest -k "test_welcome" tests/
```

### Test Markers
Tests are marked with categories for easy filtering:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow-running tests

## Prerequisites by Test Type

### Unit Tests
- ✅ No external dependencies
- ✅ Run anywhere, anytime

### Integration Tests
- 🔴 Redis server running
- 🔴 API server running (`python run.py`)
- ⚠️ Basic configuration (.env file)

### End-to-End Tests
- 🔴 Redis server running
- 🔴 API server running
- 🔴 Background worker running (`rq worker video_generation`)
- 🔴 OpenAI API key configured
- 🔴 Google Cloud TTS credentials
- 🔴 SendGrid API key (optional)
- 🔴 FFmpeg installed

## Development Workflow

### 1. During Development
```bash
# Quick feedback loop
python tests/run_tests.py unit
```

### 2. Before Committing
```bash
# Validate integration
python tests/run_tests.py quick
```

### 3. Before Deployment
```bash
# Full validation
python tests/run_tests.py setup
python tests/run_tests.py all
```

### 4. Debugging Issues
```bash
# Use utility scripts
python tests/utils/check_setup.py
python tests/utils/debug_config.py
python tests/utils/check_queue.py
```

## Writing New Tests

### Unit Test Example
```python
import pytest
from app.services.video_generator import VideoGenerator

@pytest.mark.unit
def test_slide_creation():
    video_gen = VideoGenerator()
    # Test logic here
    assert result is not None
```

### Integration Test Example
```python
import pytest
import requests

@pytest.mark.integration
def test_webhook_endpoint():
    response = requests.post("http://localhost:8000/webhooks/status")
    assert response.status_code == 200
```

### End-to-End Test Example
```python
import pytest
from app.workers.video_worker import generate_onboarding_video

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_video_generation():
    result = generate_onboarding_video(employee_data, job_id)
    assert result["success"] is True
```

## Test Data and Fixtures

### Shared Fixtures (conftest.py)
- `sample_employee_data` - Standard test employee
- `mock_webhook_payload` - Test webhook data
- `test_output_dir` - Temporary output directory

### Custom Test Data
Create test-specific data in individual test files or in the `fixtures/` directory.

## Continuous Integration

For CI/CD pipelines, use different test commands:

```yaml
# CI Pipeline Example
- name: Unit Tests
  run: python tests/run_tests.py unit

- name: Integration Tests (with services)
  run: |
    docker run -d redis:7-alpine
    python run.py &
    python tests/run_tests.py integration
```

## Troubleshooting

### Common Issues

**Tests fail with import errors**
- Ensure you're running from the project root
- Check that `conftest.py` is properly setting up the Python path

**Integration tests fail**
- Verify Redis is running: `docker ps | grep redis`
- Verify API server is running: `curl http://localhost:8000/health`

**E2E tests fail**
- Run setup validation: `python tests/run_tests.py setup`
- Check all API keys are configured
- Verify external services are accessible

### Debug Commands
```bash
# Check test discovery
pytest --collect-only

# Run with full output
pytest -s -v tests/unit/test_welcome_slide.py

# Run specific test function
pytest tests/unit/test_welcome_slide.py::test_welcome_slide_creation
```